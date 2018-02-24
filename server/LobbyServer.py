import socket
import select
import struct
import json

class Lobby(object):

    def __init__(self):
        self.address = ('', 41119)
        self.listen_num = 64
        self.message_buffer = {}    # data buffer
        self.read_list = []
        self.write_list = []
        self.except_list = []

    def startLobby(self):
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
            if len(msg) >= 4 + length:
                inst = msg[4:4 + length]
                self.operateInst(inst)
                msg = msg[4 + length:]
        self.message_buffer[sock] = msg

    def operateInst(self, inst):
        tlb = json.loads(inst)
        print tlb
        



