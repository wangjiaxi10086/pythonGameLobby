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

    def run(self):
        while True:
            self.sendProblem()
            time.sleep(5)

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
                print '{0} game problem declare in room[{1}]: {2}'.format(now_time, room_name, pro_str)
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


