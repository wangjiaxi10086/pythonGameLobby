
class Instructions:

    # instructions
    REGISTER = 1
    LOGIN = 2
    ACK = 3
    SENDTO = 4
    SENDALL = 5
    CREATE_ROOM = 6
    ENTER_ROOM = 7
    LIST_ROOM = 8
    LEAVE_ROOM = 9
    SEND_ROOM = 10
    LIST_ROOM_USER = 11
    PROBLEM = 12
    ANSWER = 13
    GAME_OVER = 14
    GAME_RESULT = 15
    KICK_OFF = 16

    # server success answer
    REGISTER_SUCCESS = 1000
    LOGIN_SUCCESS = 1001
    CREATE_ROOM_SUCCESS = 1002
    ENTER_ROOM_SUCCESS = 1003
    LEAVE_ROOM_SUCCESS = 1004
    ANSWER_SEND_SUCCESS = 1005

    # server exception answer
    USER_ALREADY_EXIST = 10000
    USER_NOT_EXIST = 10001
    WRONG_PASSWORD = 10002
    WRONG_NAME = 10003
    ROOM_ALREADY_EXIST = 10004
    ROOM_NOT_EXIST = 10005
    ALREADY_IN_ROOM = 10006
    NOT_IN_ROOM = 10007
    USER_NOT_ONLINE = 10008
    WRONG_SYNTAX_ANSWER = 10009
    ALREADY_ANSWER = 10010
    NOT_AT_ANSWER_TIME = 10011
    NONE_INPUT = 10022

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
    SOURCE = 'sour'
    MESSAGE = 'msg'
    LAST_LOGIN_TIME = 'last_login_time'
    CURRENT_ROOM = 'cur_room'
    GAME_TIME = 'gtime'
    ANSWER_RESULT = 'result'
    HAS_WINNER = 'has_winner'

    CHAT_ALL = 'chatall'
    CHAT_ROOM = 'chatroom'
    CHAT_WITH = 'chatwith'
    CREATE_ROOM = 'createroom'
    ENTER_ROOM = 'enterroom'
    LIST_ROOM = 'listroom'
    LEAVE_ROOM = 'leaveroom'
    LIST_ROOM_USER = 'listroomuser'
    HELP = 'help'
    ANSWER = 'answer'
    GAME21 = '21game'

    ALL_ROOMS = 'allroom'
    ROOM_NAME = 'rname'
    LOCATION = 'loc'
    LOBBY = 'lobby'
    ROOM_USER = 'ruser'

    def __init__(self):
        pass





