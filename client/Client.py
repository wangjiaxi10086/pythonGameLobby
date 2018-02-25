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

    def readLobbyMsg(self, inst):
        name = inst[Constant.NAME]
        msg = inst[Constant.MESSAGE]
        print '\n(Lobby) [{0}]: {1}'.format(name, msg)


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
            Instructions.SERVER_CLOSED: "Wrong! Server is Closed!",
            Instructions.WRONG_NAME: "Wrong! Name Should Nnly be Char, Digit or '_'",
        }

    def startClient(self):
        print "Client starting"
        print "Connecting to server..."
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.serv_address)

        print "Login or Register an account:"

        opt = raw_input().strip()
        while opt != "exit":
            right_input = True
            # login
            if opt.startswith("log"):
                print "Login the account:"
                name = raw_input("name:").strip()
                password = raw_input("password:").strip()
                if self.checkName(name):
                    self.login(name, password)
                else:
                    self.outputResult(Instructions.WRONG_NAME)
                    right_input = False
            # register
            elif opt.startswith("reg"):
                print "Register an account:"
                name = raw_input("name:").strip()
                password = raw_input("password:").strip()
                if self.checkName(name):
                    self.register(name, password)
                else:
                    self.outputResult(Instructions.WRONG_NAME)
                    right_input = False
            else:
                right_input = False

            if right_input:
                try:
                    data = self.sock.recv(1024)
                except socket.error as e:
                    result = Instructions.SERVER_CLOSED
                    self.closeClient()
                else:
                    if data:
                        result = self.readACK(data)
                    else:
                        result = Instructions.SERVER_CLOSED
                        self.closeClient()
                if result < 0:
                    self.outputResult(result)
                    break

            print "\nLogin or Register an account:"
            opt = raw_input().strip()

    def checkName(self, name):
        for c in name:
            if not str.isalpha(c) and not str.isdigit(c) and c != '_':
                return False
        return True

    def joinLobby(self):
        print "join to the lobby"

        in_str = raw_input(self.name + '>>> ').strip()
        if self.rcv_thread.out:
            return Instructions.SERVER_CLOSED
        while in_str != 'exit':
            # send all messages
            if in_str.startswith(Constant.CHAT_ALL):
                send_str = in_str[len(Constant.CHAT_ALL):].strip()
                self.sendAll(send_str)
            # create a new room
            elif in_str.startswith(Constant.CREATE_ROOM):
                room_name = in_str[len(Constant.CREATE_ROOM):].strip()
                if self.checkName(room_name):
                    self.createRoom(room_name)
                else:
                    self.outputResult(Instructions.WRONG_NAME)
            # enter a room
            elif in_str.startswith(Constant.ENTER_ROOM):
                room_name = in_str[len(Constant.CREATE_ROOM):].strip()
                self.enterRoom(room_name)

            in_str = raw_input(self.name + '>>> ').strip()
            if self.rcv_thread.out:
                return Instructions.SERVER_CLOSED

        return 0

    def enterRoom(self, room_name):
        tbl = {
            Constant.INSTRUCTION: Instructions.ENTER_ROOM,
            Constant.NAME: self.name,
            Constant.ROOM_NAME: room_name
        }
        tbl_str = json.dumps(tbl)
        self.sendData(tbl_str)

    def createRoom(self, room_name):
        tbl = {
            Constant.INSTRUCTION: Instructions.CREATE_ROOM,
            Constant.NAME: self.name,
            Constant.ROOM_NAME: room_name,
        }
        tbl_str = json.dumps(tbl)
        self.sendData(tbl_str)

    def sendAll(self, msg):
        tbl = {
            Constant.INSTRUCTION: Instructions.SENDALL,
            Constant.NAME: self.name,
            Constant.MESSAGE: msg
        }
        tbl_str = json.dumps(tbl)
        self.sendData(tbl_str)

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
        exit(0)

    def login(self, name, password):
        self.name = name
        tbl = {
            Constant.INSTRUCTION: Instructions.LOGIN,
            Constant.NAME: name,
            Constant.PASSWORD: password
        }
        tbl_str = json.dumps(tbl)
        # print len(tbl_str)
        self.sendData(tbl_str)

    def register(self, name, password):
        tbl = {
            Constant.INSTRUCTION: Instructions.REGISTER,
            Constant.NAME: name,
            Constant.PASSWORD: password
        }
        tbl_str = json.dumps(tbl)
        self.sendData(tbl_str)

    def sendData(self, msg_str):
        try:
            length = struct.pack('i', len(msg_str))
            data = length + msg_str
            self.sock.send(data)
        except socket.error as e:
            self.outputResult(Instructions.SERVER_CLOSED)
            exit(0)



