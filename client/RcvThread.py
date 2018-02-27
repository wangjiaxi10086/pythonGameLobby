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
        while not self.out:
            try:
                data = self.sock.recv(1024)
            except socket.error as e:
                self.sock.shutdown(socket.SHUT_WR)
                self.out = True
            else:
                if data:
                    self.msg_buf += data
                    while len(self.msg_buf) > 4:
                        length = struct.unpack('i', self.msg_buf[0:4])[0]
                        if len(self.msg_buf) < 4 + length:
                            self.out = True
                        inst = json.loads(self.msg_buf[4:4 + length])
                        self.msg_buf = self.msg_buf[4+length:]
                        self.readMsg(inst)
                else:
                    self.sock.shutdown(socket.SHUT_WR)
                    self.out = True

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
        elif inst[Constant.INSTRUCTION] == Instructions.PROBLEM:
            self.readProblem(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.GAME_OVER:
            self.gameOver(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.GAME_RESULT:
            self.gameResult(inst)
        elif inst[Constant.INSTRUCTION] == Instructions.KICK_OFF:
            self.kickoff()

    def kickoff(self):
        self.out = True
        print '\nAccount is login in other client.'

    def gameResult(self, inst):
        has_winner = inst[Constant.HAS_WINNER]
        room_name = inst[Constant.ROOM_NAME]

        if has_winner:
            win_name = inst[Constant.NAME]
            answer = inst[Constant.ANSWER]
            print '\n(Room: {0}) [{1}] Win! Answer: [{2}]'.format(room_name, win_name, answer)
        else:
            print '\n(Room: {0}) Nobody Win!'.format(room_name)

    def gameOver(self, inst):
        room_name = inst[Constant.ROOM_NAME]
        server_time = inst[Constant.GAME_TIME]
        print '\n{0} (Room: {1}) Game Over!'.format(server_time, room_name)

    def readProblem(self, inst):
        game_time = inst[Constant.GAME_TIME]
        room_name = inst[Constant.ROOM_NAME]
        pro_msg = inst[Constant.MESSAGE]
        print '\n{0} (Room: {1}) Game Problem: {2}'.format(game_time, room_name, pro_msg)

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
        # room is already existed
        if inst[Constant.FEEDBACK] == Instructions.ROOM_ALREADY_EXIST:
            print '\n(Server) Room [{0}] is already existed.'.format(inst[Constant.ROOM_NAME])
        # create room in server successfully
        elif inst[Constant.FEEDBACK] == Instructions.CREATE_ROOM_SUCCESS:
            print '\n(Server) Room [{0}] creates successfully.'.format(inst[Constant.ROOM_NAME])
            print '(Server) Enter room [{0}]'.format(inst[Constant.ROOM_NAME])
        # user is already in a room
        elif inst[Constant.FEEDBACK] == Instructions.ALREADY_IN_ROOM:
            print '\n(Server) Already in room: [{0}].'.format(inst[Constant.ROOM_NAME])
        # the room doesn't exist
        elif inst[Constant.FEEDBACK] == Instructions.ROOM_NOT_EXIST:
            print "\n(Server) Room [{0}] doesn't exist.".format(inst[Constant.ROOM_NAME])
        # enter room successfully
        elif inst[Constant.FEEDBACK] == Instructions.ENTER_ROOM_SUCCESS:
            print '\n(Server) Enter room [{0}] successfully'.format(inst[Constant.ROOM_NAME])
        # leave room successfully
        elif inst[Constant.FEEDBACK] == Instructions.LEAVE_ROOM_SUCCESS:
            print '\n(Server) Leave room[{0}] successfully'.format(inst[Constant.ROOM_NAME])
        # user is not in any room now
        elif inst[Constant.FEEDBACK] == Instructions.NOT_IN_ROOM:
            print '\n(Server) Not in any room now.'
        # the user is not online
        elif inst[Constant.FEEDBACK] == Instructions.USER_NOT_ONLINE:
            print '\n(Server) User {0} is not online.'.format(inst[Constant.DESTINATION])
        # the answer syntax is wrong
        elif inst[Constant.FEEDBACK] == Instructions.WRONG_SYNTAX_ANSWER:
            print '\n(Server) The answer syntax is wrong!'
        # answer send to server successfully
        elif inst[Constant.FEEDBACK] == Instructions.ANSWER_SEND_SUCCESS:
            print '\n(Server) Server receive answer successfully.'
        # user has already answer this problem
        elif inst[Constant.FEEDBACK] == Instructions.ALREADY_ANSWER:
            print '\n(Server) You have already answer in this room.'
        # not at a answer time
        elif inst[Constant.FEEDBACK] == Instructions.NOT_AT_ANSWER_TIME:
            print '\n(Server) It\'s not at answer time now.'

    def listRoom(self, inst):
        room_list = inst[Constant.ALL_ROOMS]
        if len(room_list) == 0:
            print'\n(Server) There is none rooms in the server.'
        else:
            print '\n(Server) Rooms in Server:'
            for room_name in room_list:
                print '[{0}], '.format(room_name),
            print ''


