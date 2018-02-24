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
        print "Lobby is starting"
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
        print "closing", sock.getpeername()
        if sock in self.read_list:
            self.read_list.remove(sock)
        if sock in self.message_buffer.keys():
            self.message_buffer.pop(sock)
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
        tlb = json.loads(inst)
        print tlb
        if Constant.INSTRUCTION in tlb.keys():
            if tlb[Constant.INSTRUCTION] == Instructions.REGISTER:
                self.user_register(sock, tlb)
            elif tlb[Constant.INSTRUCTION] == Instructions.LOGIN:
                pass

    def user_register(self, sock, inst):
        if not os.path.exists(self.user_path):
            os.mkdir(self.user_path)
        user_list = os.listdir(self.user_path)
        name = inst[Constant.NAME]
        if name in user_list:
            # user name is already exists
            tbl = {
                Constant.FEEDBACK: Instructions.USER_ALREADY_EXIST,
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
                Constant.FEEDBACK: Instructions.SUCCESS,
            }
        back_data = json.dumps(tbl)
        length = struct.pack('i', len(back_data))
        sock.send(length + back_data)




