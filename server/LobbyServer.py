import socket
import select
import struct
import json
import os
import datetime
from Instruction import Instructions
from Instruction import Constant


class Lobby(object):

    def __init__(self):
        self.address = ('', 41119)
        self.listen_num = 64

        self.message_buffer = {}    # data buffer
        self.user_data = {}         # sock -> user data
        self.user_sock = {}         # name -> sock

        self.room_list = {}         # room name -> user list of this room

        self.read_list = []
        self.write_list = []
        self.except_list = []

        self.user_path = os.getcwd() + "\\userdata"
        if not os.path.exists(self.user_path):
            os.mkdir(self.user_path)

    def startLobby(self):
        print "Lobby is starting..."
        listenfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listenfd.bind(self.address)
        listenfd.listen(self.listen_num)

        self.read_list.append(listenfd)

        while True:
            # use select to support multi clients
            read_set, write_set, except_set = select.select(self.read_list, self.write_list, self.except_list)

            for sock in read_set:
                if sock is listenfd:
                    connfd, client_addr = sock.accept()
                    print "connect from ", connfd.getpeername()
                    self.read_list.append(connfd)
                    self.message_buffer[sock] = ""
                else:
                    try:
                        data = sock.recv(1024)
                    except socket.error as e:
                        self.closeClient(sock)
                    else:
                        if data:
                            self.readData(sock, data)
                        else:
                            self.closeClient(sock)

    def closeClient(self, sock):
        print "socket closing", sock.getpeername()
        if sock in self.read_list:
            self.read_list.remove(sock)
        if sock in self.message_buffer.keys():
            self.message_buffer.pop(sock)
        if sock in self.user_data.keys():
            user_data = self.user_data[sock]
            user_name = user_data[Constant.NAME]
            cur_room = user_data[Constant.CURRENT_ROOM]
            user_data[Constant.CURRENT_ROOM] = None

            now_time = datetime.datetime.now()
            timeval = (now_time - user_data[Constant.LAST_LOGIN_TIME]).total_seconds()
            user_data[Constant.TIMEVAL] += timeval
            # change last login time for json dumps
            user_data[Constant.LAST_LOGIN_TIME] = user_data[Constant.LAST_LOGIN_TIME].strftime('%Y-%m-%d %H:%M:%S')

            # user leave current room
            self.outofRoom(sock, cur_room)
            self.user_data.pop(sock)
            self.user_sock.pop(user_name)

            # update user data to file
            with open(self.user_path + '\\' + user_name, 'w') as user_file:
                data_str = json.dumps(user_data)
                user_file.write(data_str)
        sock.close()

    def readData(self, sock, data):
        if sock not in self.message_buffer.keys():
            self.message_buffer[sock] = ""
        self.message_buffer[sock] += data
        msg = self.message_buffer[sock]
        while len(msg) > 4:
            length = struct.unpack('i', data[0:4])[0]
            if len(msg) < 4 + length:
                break
            inst = msg[4:4 + length]
            self.operateInst(sock, inst)
            msg = msg[4 + length:]
        self.message_buffer[sock] = msg

    def operateInst(self, sock, inst):
        tbl = json.loads(inst)
        if Constant.INSTRUCTION in tbl.keys():
            if tbl[Constant.INSTRUCTION] == Instructions.REGISTER:
                self.userRegister(sock, tbl)
            elif tbl[Constant.INSTRUCTION] == Instructions.LOGIN:
                self.userLogin(sock, tbl)
            elif tbl[Constant.INSTRUCTION] == Instructions.SENDALL:
                self.sendALL(sock, tbl)
            elif tbl[Constant.INSTRUCTION] == Instructions.CREATE_ROOM:
                self.createRoom(sock, tbl)
            elif tbl[Constant.INSTRUCTION] == Instructions.ENTER_ROOM:
                self.enterRoom(sock, tbl)
            elif tbl[Constant.INSTRUCTION] == Instructions.LIST_ROOM:
                self.listRoom(sock, tbl)

    def listRoom(self, sock, inst):
        if sock in self.user_data.keys():
            print '[{0}] list all rooms.'.format(inst[Constant.NAME])
            tbl = {
                Constant.INSTRUCTION: Instructions.LIST_ROOM,
                Constant.ALL_ROOMS: self.room_list.keys(),
            }
            send_data = json.dumps(tbl)
            self.sendMsg(sock, send_data)

    def enterRoom(self, sock, inst):
        if sock in self.user_data.keys():
            print '[{0}] enter room: [{1}].'.format(inst[Constant.NAME], inst[Constant.ROOM_NAME])
            room_name = inst[Constant.ROOM_NAME]

            tbl = {
                Constant.INSTRUCTION: Instructions.ACK,
                Constant.ROOM_NAME: room_name
            }
            if room_name in self.room_list.keys():
                if Constant.CURRENT_ROOM in self.user_data[sock].keys():
                    old_room = self.user_data[sock][Constant.CURRENT_ROOM]
                else:
                    old_room = None

                # if user already in this room
                if old_room == room_name:
                    tbl[Constant.FEEDBACK] = Instructions.ALREADY_IN_ROOM
                # enter new room
                else:
                    self.outofRoom(sock, old_room)
                    self.room_list[room_name].append(sock)
                    print "room list: ", self.room_list
                    self.user_data[sock][Constant.CURRENT_ROOM] = room_name
                    tbl[Constant.FEEDBACK] = Instructions.ENTER_ROOM_SUCCESS
            # if room doesn't exists
            else:
                tbl[Constant.FEEDBACK] = Instructions.ROOM_NOT_EXIST
            send_data = json.dumps(tbl)
            self.sendMsg(sock, send_data)


    def outofRoom(self, sock, room_name):
        # leave the current room, if on one in this room, then delete this room
        if room_name and room_name in self.room_list:
            self.room_list[room_name].remove(sock)
            if len(self.room_list[room_name]) == 0:
                self.room_list.pop(room_name)

    def createRoom(self, sock, inst):
        if sock in self.user_data.keys():
            print '[{0}] create room: [{1}].'.format(inst[Constant.NAME], inst[Constant.ROOM_NAME])
            room_name = inst[Constant.ROOM_NAME]
            # room is already exists
            if room_name in self.room_list.keys():
                tbl = {
                    Constant.INSTRUCTION: Instructions.ACK,
                    Constant.FEEDBACK: Instructions.ROOM_ALREADY_EXIST,
                    Constant.ROOM_NAME: room_name
                }
            # create new room and this user enter the new room
            else:
                # leave old room
                if Constant.CURRENT_ROOM in self.user_data[sock].keys():
                    old_room = self.user_data[sock][Constant.CURRENT_ROOM]
                else:
                    old_room = None
                self.outofRoom(sock, old_room)

                # create new room
                self.room_list[room_name] = [sock]
                print "room list: ", self.room_list
                self.user_data[sock][Constant.CURRENT_ROOM] = room_name

                tbl = {
                    Constant.INSTRUCTION: Instructions.ACK,
                    Constant.FEEDBACK: Instructions.CREATE_ROOM_SUCCESS,
                    Constant.ROOM_NAME: room_name
                }
            send_data = json.dumps(tbl)
            self.sendMsg(sock, send_data)


    def sendALL(self, sock, inst):
        # ensure user is already login
        if sock in self.user_data.keys():
            print '[{0}] send all message: [{1}]'.format(inst[Constant.NAME], inst[Constant.MESSAGE])
            tbl = {
                Constant.INSTRUCTION: Instructions.SENDALL,
                Constant.NAME: inst[Constant.NAME],
                Constant.MESSAGE: inst[Constant.MESSAGE],
                Constant.LOCATION: Constant.LOBBY
            }
            send_data = json.dumps(tbl)
            for user in self.user_data.keys():
                # send message to everyone except oneself
                if user != sock:
                    self.sendMsg(user, send_data)

    def userLogin(self, sock, inst):
        name = inst[Constant.NAME]
        print "user", sock.getpeername(), "login with name:", name
        password = inst[Constant.PASSWORD]
        if name in self.user_sock.keys():
            # user is already login
            old_sock = self.user_sock[name]
            # close old sock
            self.closeClient(old_sock)

            with open(self.user_path + '\\' + name, 'r') as user_file:
                user_data = json.loads(user_file.read())

            self.user_sock[name] = sock
            self.user_data[sock] = user_data
            self.user_data[sock][Constant.LAST_LOGIN_TIME] = datetime.datetime.now()

            tbl = {
                Constant.FEEDBACK: Instructions.LOGIN_SUCCESS,
                Constant.INSTRUCTION: Instructions.ACK
            }

        else:
            if not os.path.exists(self.user_path):
                os.mkdir(self.user_path)
            user_list = os.listdir(self.user_path)

            if name in user_list:
                with open(self.user_path + '\\' + name, 'r') as user_file:
                    user_data = json.loads(user_file.read())
                if password == user_data[Constant.PASSWORD]:
                    # login success
                    tbl = {
                        Constant.FEEDBACK: Instructions.LOGIN_SUCCESS,
                        Constant.INSTRUCTION: Instructions.ACK
                    }
                    self.user_sock[name] = sock
                    self.user_data[sock] = user_data
                    self.user_data[sock][Constant.LAST_LOGIN_TIME] = datetime.datetime.now()
                    self.user_data[sock][Constant.CURRENT_ROOM] = None
                else:
                    # password is wrong
                    tbl = {
                        Constant.FEEDBACK: Instructions.WRONG_PASSWORD,
                        Constant.INSTRUCTION: Instructions.ACK
                    }
            else:
                # user is not exist
                tbl = {
                    Constant.FEEDBACK: Instructions.USER_NOT_EXIST,
                    Constant.INSTRUCTION: Instructions.ACK
                }
        back_data = json.dumps(tbl)
        self.sendMsg(sock, back_data)

    def userRegister(self, sock, inst):
        print "user register from", sock.getpeername()
        if not os.path.exists(self.user_path):
            os.mkdir(self.user_path)
        user_list = os.listdir(self.user_path)
        name = inst[Constant.NAME]
        if name in user_list:
            # user name is already exists
            tbl = {
                Constant.FEEDBACK: Instructions.USER_ALREADY_EXIST,
                Constant.INSTRUCTION: Instructions.ACK
            }
        else:
            with open(self.user_path + '\\' + name, 'w') as user_file:
                user_data = {
                    Constant.NAME: inst[Constant.NAME],
                    Constant.PASSWORD: inst[Constant.PASSWORD],
                    Constant.TIMEVAL: 0.0,
                }
                user_str = json.dumps(user_data)
                user_file.write(user_str)
            tbl = {
                Constant.FEEDBACK: Instructions.REGISTER_SUCCESS,
                Constant.INSTRUCTION: Instructions.ACK
            }
        back_data = json.dumps(tbl)
        self.sendMsg(sock, back_data)

    def sendMsg(self, sock, data):
        length = struct.pack('i', len(data))
        sock.send(length + data)




