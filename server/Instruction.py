

class Instructions:

    REGISTER = 1
    LOGIN = 2
    ACK = 3
    SEND = 4
    SENDALL = 5

    REGISTER_SUCCESS = 1000
    LOGIN_SUCCESS = 1001

    USER_ALREADY_EXIST = 10000
    USER_NOT_EXIST = 10001
    WRONG_PASSWORD = 10002

    SERVER_CLOSED = -1
    WRONG_DATA = -2

    def __init__(self):
        pass


class Constant:

    NAME = 'name'
    INSTRUCTION = 'inst'
    PASSWORD = 'pass'
    TIMEVAL = 'timeval'
    FEEDBACK = 'feedback'
    DESTINATION = 'dest'
    MESSAGE = 'msg'

    def __init__(self):
        pass





