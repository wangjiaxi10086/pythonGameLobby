import json
import struct
import threading
import socket
import time
import  random
import datetime
from Instruction import Instructions
from Instruction import Constant


class GameThread(threading.Thread):

    def __init__(self, room_list, user_data):
        threading.Thread.__init__(self)
        self.room_list = room_list
        self.user_data = user_data

        self.user_answer = {}
        self.already_answer = []

        self.at_answer_time = False
        self.send_problem_list = []

    def run(self):
        while True:
            self.send_problem_list = self.room_list.keys()
            self.sendProblem()
            self.at_answer_time = True
            time.sleep(30)

            self.gameOver()
            self.at_answer_time = False
            self.sendGameResult()

            self.user_answer = {}
            self.already_answer = []
            self.send_problem_list = []

            time.sleep(15)

    def sendGameResult(self):
        for room_name in self.send_problem_list:
            if room_name in self.user_answer.keys():
                user_ans = self.user_answer[room_name]
                if len(user_ans) == 0:
                    tbl = {
                        Constant.INSTRUCTION: Instructions.GAME_RESULT,
                        Constant.HAS_WINNER: False,
                        Constant.ROOM_NAME: room_name
                    }
                else:
                    print user_ans
                    max_result = -1
                    max_user = None
                    for i in range(0, len(user_ans)):
                        result = user_ans[i][Constant.ANSWER_RESULT]
                        if 21 >= result > max_result:
                            max_user = user_ans[i]
                            max_result = result
                    tbl = {
                        Constant.INSTRUCTION: Instructions.GAME_RESULT,
                        Constant.HAS_WINNER: True,
                        Constant.NAME: max_user[Constant.NAME],
                        Constant.ANSWER: max_user[Constant.ANSWER],
                        Constant.ROOM_NAME: room_name
                    }
                send_data = json.dumps(tbl)
                for user_sock in self.room_list[room_name]:
                    length = struct.pack('i', len(send_data))
                    user_sock.send(length + send_data)

    def out_of_room(self, sock, room_name):
        if sock in self.user_data.keys():
            user_name = self.user_data[sock][Constant.NAME]
            if user_name in self.already_answer:
                self.already_answer.remove(user_name)
                if room_name in self.user_answer.keys():
                    loc = 0
                    for i in range(len(self.user_answer[room_name])):
                        if user_name[room_name][i][Constant.NAME] == room_name:
                            loc = i
                    self.user_answer[room_name].pop(loc)

    def deleteRoom(self, room_name):
        if room_name in self.send_problem_list:
            self.send_problem_list.remove(room_name)
        if room_name in self.user_answer.keys():
            self.user_answer.pop(room_name)

    def gameOver(self):
        now_time = datetime.datetime.now().strftime('%H:%M:%S')
        for room_name in self.send_problem_list:
            user_list = self.room_list[room_name]
            if len(user_list) > 0:
                print '{0} game over in room[{1}]'.format(now_time, room_name)
                tbl = {
                    Constant.INSTRUCTION: Instructions.GAME_OVER,
                    Constant.ROOM_NAME: room_name,
                    Constant.GAME_TIME: now_time
                }
                send_data = json.dumps(tbl)
                for user_sock in user_list:
                    length = struct.pack('i', len(send_data))
                    user_sock.send(length + send_data)

    def receiveAnswer(self, sock, inst):
        user_name = inst[Constant.NAME]
        answer = inst[Constant.ANSWER]
        if Constant.CURRENT_ROOM in self.user_data[sock].keys():
            cur_room = self.user_data[sock][Constant.CURRENT_ROOM]
        else:
            cur_room = None

        if cur_room:
            print 'Receive answer from {0} in Room {1}: [{2}]'.format(user_name, cur_room, answer)
            try:
                result = eval(answer)
            # wrong syntax of answer
            except SyntaxError:
                tbl = {
                    Constant.INSTRUCTION: Instructions.ACK,
                    Constant.FEEDBACK: Instructions.WRONG_SYNTAX_ANSWER
                }
            else:
                if self.at_answer_time:
                    user_ans = {Constant.NAME: user_name, Constant.ANSWER_RESULT: result, Constant.ANSWER: answer}
                    if cur_room not in self.user_answer.keys():
                        self.user_answer[cur_room] = [user_ans]
                        self.already_answer.append(user_name)
                        tbl = {
                            Constant.INSTRUCTION: Instructions.ACK,
                            Constant.FEEDBACK: Instructions.ANSWER_SEND_SUCCESS
                        }
                    else:
                        if user_name in self.already_answer:
                            tbl = {
                                Constant.INSTRUCTION: Instructions.ACK,
                                Constant.FEEDBACK: Instructions.ALREADY_ANSWER
                            }
                        else:
                            self.user_answer[cur_room].append(user_ans)
                            tbl = {
                                Constant.INSTRUCTION: Instructions.ACK,
                                Constant.FEEDBACK: Instructions.ANSWER_SEND_SUCCESS
                            }
                            self.already_answer.append(user_name)
                else:
                    tbl = {
                        Constant.INSTRUCTION: Instructions.ACK,
                        Constant.FEEDBACK: Instructions.NOT_AT_ANSWER_TIME
                    }
        else:
            tbl = {
                Constant.INSTRUCTION: Instructions.ACK,
                Constant.FEEDBACK: Instructions.NOT_IN_ROOM
            }
        send_data = json.dumps(tbl)
        length = struct.pack('i', len(send_data))
        sock.send(length + send_data)

    def generateProblem(self):
        result = ""
        for i in range(4):
            x = random.randint(1, 10)
            result += str(x) + ' '
        return result

    def sendProblem(self):
        now_time = datetime.datetime.now().strftime('%H:%M:%S')
        for room_name, user_list in self.room_list.iteritems():
            if len(user_list) > 0:
                pro_str = self.generateProblem()
                print '{0} game declared in room[{1}]: {2}'.format(now_time, room_name, pro_str)
                tbl = {
                    Constant.INSTRUCTION: Instructions.PROBLEM,
                    Constant.MESSAGE: pro_str,
                    Constant.ROOM_NAME: room_name,
                    Constant.GAME_TIME: now_time
                }
                send_data = json.dumps(tbl)
                for user_sock in user_list:
                    length = struct.pack('i', len(send_data))
                    user_sock.send(length + send_data)


