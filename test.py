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

    print range(1,1)
