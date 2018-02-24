import socket
import json
import struct
from Instruction import Instructions

class Client(object):

    def __init__(self):
        self.serv_address = ("127.0.0.1", 41119)

    def startClient(self):
        print "Client starting"
        print "Connecting to server..."
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_address)

        print "Login or Register an account."

        opt = raw_input()
        while opt != "exit":
            #login
            if opt.startswith("log"):
                print "Login the account:"
                name = raw_input("name:").strip()
                password = raw_input("password:").strip()
                self.login(name, password)
            #register
            elif opt.startswith("reg"):
                print "Register an account:"
                name = raw_input("name:").strip()
                password = raw_input("password:").strip()
                self.register(name, password)
            else:
                break
            opt = input()

    def login(self, name, password):
        tbl = {'inst': Instructions.LOGIN, 'name': name, 'pass': password}
        tbl_str = json.dumps(tbl)
        # print len(tbl_str)
        length = struct.pack('i', len(tbl_str))
        data = length + tbl_str
        self.sock.send(data)

    def register(self, name, password):
        tbl = {'inst': Instructions.REGISTER, 'name': name, 'pass': password}
        tbl_str = json.dumps(tbl)
        length = struct.pack('i', len(tbl_str))
        data = length + tbl_str
        self.sock.send(data)


