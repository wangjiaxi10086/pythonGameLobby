import json
import struct
import threading
import socket
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
        if inst[Constant.INSTRUCTION] == Instructions.SENDALL:
            self.readLobbyMsg(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.LIST_ROOM:
            self.listRoom(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.ACK:
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

    def listRoom(self, inst):
        room_list = inst[Constant.ALL_ROOMS]
        if len(room_list) == 0:
            print'\n(Server) There is none rooms in the server.'
        else:
            print '\n(Server) Rooms in Server:'
            for room_name in room_list:
                print '[{0}], '.format(room_name),
            print ''

    def readLobbyMsg(self, inst):
        name = inst[Constant.NAME]
        msg = inst[Constant.MESSAGE]
        print '\n(Lobby) [{0}]: {1}'.format(name, msg)
