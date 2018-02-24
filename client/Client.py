import socket
import json
import struct
from Instruction import Instructions
from Instruction import Constant

class Client(object):

    def __init__(self):
        self.serv_address = ("127.0.0.1", 41119)
        self.msg_buf = ""

    def startClient(self):
        print "Client starting"
        print "Connecting to server..."
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_address)
        print "Login or Register an account."

        opt = raw_input().strip()
        while opt != "exit":
            # login
            if opt.startswith("log"):
                print "Login the account:"
                name = raw_input("name:").strip()
                password = raw_input("password:").strip()
                self.login(name, password)
            # register
            elif opt.startswith("reg"):
                print "Register an account:"
                name = raw_input("name:").strip()
                password = raw_input("password:").strip()
                self.register(name, password)
            else:
                break

            try:
                data = self.sock.recv(1024)
            except socket.error as e:
                print "Server closed"
                result = Instructions.SERVER_CLOSED
                self.closeClient()
            else:
                if data:
                    result = self.readFeedback(data)
                else:
                    print "Server closed"
                    self.closeClient()
                    result = Instructions.SERVER_CLOSED
            if result < 0:
                break

            print "Login or Register an account."
            opt = raw_input().strip()


    def readFeedback(self, data):
        self.msg_buf += data
        if len(self.msg_buf) > 4:
            length = struct.unpack('i', self.msg_buf[0:4])[0]
            if len(self.msg_buf) < 4 + length:
                return Instructions.WRONG_DATA
            tlb = json.loads(self.msg_buf[4:4+length])
            print tlb
            self.msg_buf = self.msg_buf[4+length:]
            result = tlb[Constant.FEEDBACK]
            if result == Instructions.SUCCESS:
                print "Register Successfully"
            elif result == Instructions.USER_ALREADY_EXIST:
                print "Wrong! Name Already Exists!"
        else:
            result = Instructions.WRONG_DATA
        return result


    def closeClient(self):
        self.sock.close()

    def login(self, name, password):
        tbl = {
            Constant.INSTRUCTION: Instructions.LOGIN,
            Constant.NAME: name,
            Constant.PASSWORD: password
        }
        tbl_str = json.dumps(tbl)
        # print len(tbl_str)
        length = struct.pack('i', len(tbl_str))
        data = length + tbl_str
        self.sock.send(data)

    def register(self, name, password):
        tbl = {
            Constant.INSTRUCTION: Instructions.REGISTER,
            Constant.NAME: name,
            Constant.PASSWORD: password
        }
        tbl_str = json.dumps(tbl)
        length = struct.pack('i', len(tbl_str))
        data = length + tbl_str
        self.sock.send(data)


