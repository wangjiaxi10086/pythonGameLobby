import socket
import select
import struct
import json
import os
from Instruction import Instructions
from Instruction import Constant


class Lobby(object):

    def __init__(self):
        self.address = ('', 41119)
        self.listen_num = 64

        self.message_buffer = {}    # data buffer
        self.user_data = {}         # store user data
        self.user_sock = {}

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
                print "user register from", sock.getpeername()
                self.userRegister(sock, tbl)
            elif tbl[Constant.INSTRUCTION] == Instructions.LOGIN:
                print "user", sock.getpeername(), "login"
                self.userLogin(sock, tbl)

    def userLogin(self, sock, inst):

        name = inst[Constant.NAME]
        password = inst[Constant.PASSWORD]
        if name in self.user_sock.keys():
            # user is already login
            old_sock = self.user_sock[name]
            user_data = self.user_data[old_sock]
            # close old sock
            self.closeClient(old_sock)

            self.user_sock[name] = sock
            self.user_data[sock] = user_data

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




