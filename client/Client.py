import socket
import json
import struct
import threading
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
                break
            else:
                if data:
                    self.msg_buf += data
                    # while len(self.msg_buf) > 4:
                    #     length = struct.unpack('i', self.msg_buf[0:4])[0]
                    #     if len(self.msg_buf) < 4 + length:
                    #         break
                    #     inst = json.loads(self.msg_buf[4:4 + length])
                    #     self.msg_buf = self.msg_buf[4+length:]
                    #     print inst
                    print '\nmessage from server:'+data
                else:
                    self.sock.shutdown(socket.SHUT_WR)

class Client(object):

    def __init__(self):
        self.serv_address = ("127.0.0.1", 41119)
        self.msg_buf = ""
        self.Words = {
            Instructions.REGISTER_SUCCESS: "Register Successfully!",
            Instructions.LOGIN_SUCCESS: "Login in Successfully!",
            Instructions.USER_ALREADY_EXIST: "Wrong! Name Already Exists!",
            Instructions.WRONG_DATA: "Wrong! Data is Broken",
            Instructions.USER_NOT_EXIST: "Wrong! User doesn't Exist!",
            Instructions.WRONG_PASSWORD: "Wrong! Password is Wrong!",
        }

    def startClient(self):
        print "Client starting"
        print "Connecting to server..."
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_address)

        print "Login or Register an account:"

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
                    result = self.readACK(data)
                else:
                    print "Server closed"
                    self.closeClient()
                    result = Instructions.SERVER_CLOSED
            if result < 0:
                break

            print "\nLogin or Register an account:"
            opt = raw_input().strip()


    def joinLobby(self):
        self.sendAll('Hello')

    def sendAll(self, msg):
        tbl = {
            Constant.INSTRUCTION: Instructions.SENDALL,
            Constant.NAME: self.name,
            Constant.MESSAGE: msg
        }
        tbl_str = json.dumps(tbl)
        length = struct.pack('i', len(tbl_str))
        data = length + tbl_str
        self.sock.send(data)

    def readACK(self, data):
        self.msg_buf += data
        if len(self.msg_buf) > 4:
            length = struct.unpack('i', self.msg_buf[0:4])[0]
            if len(self.msg_buf) < 4 + length:
                return Instructions.WRONG_DATA
            tlb = json.loads(self.msg_buf[4:4 + length])

            self.msg_buf = self.msg_buf[4 + length:]
            result = tlb[Constant.FEEDBACK]
            self.outputResult(result)

            if result == Instructions.LOGIN_SUCCESS:
                # login in successfully, into the lobby
                print "join to the lobby"
                self.rcv_thread = RcvThread(self.msg_buf, self.sock)
                self.msg_buf = ""
                self.rcv_thread.start()
                result = self.joinLobby()
        else:
            result = Instructions.WRONG_DATA
            self.outputResult(result)
        return result

    def outputResult(self, result):
        if result in self.Words.keys():
            print self.Words[result]

    def closeClient(self):
        self.sock.close()

    def login(self, name, password):
        self.name = name
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


