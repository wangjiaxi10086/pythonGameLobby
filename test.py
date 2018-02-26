import struct
import json
import os
import datetime
import time
import sched
import random


def task(schedule):
    print datetime.datetime.now()
    schedule.enter(2, 0, task, (schedule,))

if __name__ == '__main__':

    for i in range(3):
        print random.randint(1, 10),
