import json
import struct
import threading
import socket
import datetime
from Instruction import Instructions
from Instruction import Constant


class RcvThread(threading.Thread):

    def __init__(self, msg_buf, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        self.msg_buf = msg_buf
        self.out = False

    def run(self):
        while True:
            try:
                data = self.sock.recv(1024)
            except socket.error as e:
                self.sock.shutdown(socket.SHUT_WR)
                self.out = True
                break
            else:
                if data:
                    self.msg_buf += data
                    while len(self.msg_buf) > 4:
                        length = struct.unpack('i', self.msg_buf[0:4])[0]
                        if len(self.msg_buf) < 4 + length:
                            break
                        inst = json.loads(self.msg_buf[4:4 + length])
                        self.msg_buf = self.msg_buf[4+length:]
                        self.readMsg(inst)
                else:
                    self.sock.shutdown(socket.SHUT_WR)
                    self.out = True
                    break

    def readMsg(self, inst):
        self.time_now = datetime.datetime.now().strftime('%H:%M:%S')
        if inst[Constant.INSTRUCTION] == Instructions.SENDALL:
            self.readLobbyMsg(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.SEND_ROOM:
            self.readRoomMsg(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.LIST_ROOM:
            self.listRoom(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.ACK:
            self.optAck(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.LIST_ROOM_USER:
            self.listRoomUser(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.SENDTO:
            self.readPrivateMsg(inst)

    def readPrivateMsg(self, inst):
        sour_name = inst[Constant.NAME]
        msg = inst[Constant.MESSAGE]
        print '\n{0} (Private) [{1}]: {2}'.format(self.time_now, sour_name, msg)

    def listRoomUser(self, inst):
        user_list = inst[Constant.ROOM_USER]
        room_name = inst[Constant.ROOM_NAME]
        if len(user_list) == 0:
            print'\n(Server) There is none users in this room.'
        else:
            print '\n(Server) Users in Room[{0}]:'.format(room_name)
            for user_name in user_list:
                print '[{0}], '.format(user_name),
            print ''

    def readRoomMsg(self, inst):
        name = inst[Constant.NAME]
        msg = inst[Constant.MESSAGE]
        room_name = inst[Constant.ROOM_NAME]
        print '\n{0} (Room: {1}) [{2}]: {3}'.format(self.time_now, room_name, name, msg)

    def readLobbyMsg(self, inst):
        name = inst[Constant.NAME]
        msg = inst[Constant.MESSAGE]
        print '\n{0} (Lobby) [{1}]: {2}'.format(self.time_now, name, msg)

    def optAck(self, inst):
        if inst[Constant.FEEDBACK] == Instructions.ROOM_ALREADY_EXIST:
            print '\n(Server) Room [{0}] is already existed.'.format(inst[Constant.ROOM_NAME])
        elif inst[Constant.FEEDBACK] == Instructions.CREATE_ROOM_SUCCESS:
            print '\n(Server) Room [{0}] creates successfully.'.format(inst[Constant.ROOM_NAME])
        elif inst[Constant.FEEDBACK] == Instructions.ALREADY_IN_ROOM:
            print '\n(Server) Already in room: [{0}].'.format(inst[Constant.ROOM_NAME])
        elif inst[Constant.FEEDBACK] == Instructions.ROOM_NOT_EXIST:
            print "\n(Server) Room [{0}] doesn't exist.".format(inst[Constant.ROOM_NAME])
        elif inst[Constant.FEEDBACK] == Instructions.ENTER_ROOM_SUCCESS:
            print '\n(Server) Enter room [{0}] successfully'.format(inst[Constant.ROOM_NAME])
        elif inst[Constant.FEEDBACK] == Instructions.LEAVE_ROOM_SUCCESS:
            print '\n(Server) Leave room[{0}] successfully'.format(inst[Constant.ROOM_NAME])
        elif inst[Constant.FEEDBACK] == Instructions.NOT_IN_ROOM:
            print '\n(Server) Not in any room now.'
        elif inst[Constant.FEEDBACK] == Instructions.USER_NOT_ONLINE:
            print '\n(Server) user {0} is not online.'.format(inst[Constant.DESTINATION])

    def listRoom(self, inst):
        room_list = inst[Constant.ALL_ROOMS]
        if len(room_list) == 0:
            print'\n(Server) There is none rooms in the server.'
        else:
            print '\n(Server) Rooms in Server:'
            for room_name in room_list:
                print '[{0}], '.format(room_name),
            print ''


