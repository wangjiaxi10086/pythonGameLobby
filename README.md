# 项目介绍

使用python2.7制作的游戏大厅，实现效果如下：
+ 客户端可以注册新用户，用户名标识为唯一的ID。
+ 客户端可以使用帐户名，密码登陆游戏大厅。如果此时大厅中已经存在该用户，则将先前的用户踢下线。用户名只能是字母、数字和下划线的组合。
+ 用户数据通过文件的形式储存在服务端，服务器会记录每个用户总的在线时长和上次的登陆时间。
+ 用户可以在大厅中创建房间，加入房间，退出房间等。用户在创建房间时会自动加入房间。
    + 服务器如果检测到一个房间中没有一个玩家存在的话，则自动将该房间清除。
+  支持多频道聊天。
    + 用户可以向大厅中发送消息，服务器的所有用户（除了本人）都将收到该消息。
    + 用户可以向当前的房间中发送消息，房间中的所有用户（除了本人）都将收到该消息。
    + 用户还可以私聊，向特定用户发送消息。只有特定用户会收到该消息。
+ 21 点游戏
    + 服务器中每个房间每到分钟整点（例如：00：01，23：59等）会随机生成4个1到10的数，发布在房间内，房间中的所有人可以看到。（便于测试将题目公布时间设置为了分钟整点，更改相应计时函数后即可设置为半点发布，如8点，8点半等）
    + 玩家可以使用+，-，*，/和（），让4个数的结果尽量等于21，但不能超过21。
    + 玩家可以向服务端提供回答。例如发送：`21game (2 + 3) * 4  + 1`。服务器只接受玩家在该房间的第一次回答，此回答其他玩家看不到。
    + 房间中发布问题后，有30秒的答题时间，如果期间有玩家回答等于21，那么此玩家获胜，否则计时结束后，计算结果最大的玩家获胜，如果有相同答案，则取第一个回答者。30秒后服务器会向此时在房间中的玩家公布游戏结果，并公布胜利玩家的答案。
    + 玩家如果在问题结束前退出房间，则视为弃权，此时服务器将不会向玩家发送游戏结果。
    + 服务器会检测玩家发送的数字和房间中的题目是否匹配，如果出现不一样的数字，或者数字个数不正确，则视为错误答案。
    + 如果不在规定时间内答题，或者此时玩家没有进入任何房间，玩家的答题信息不会被服务器当作题目答案处理。

# 项目运行及操作

## 开启服务端
进入`server`目录下，运行
```
python main.py
```

## 开启客户端
进入`client`目录下，运行
```
python main.py
```

## 客户端命令

> tips: 因为客户端接收消息是单开的线程，所以收到服务器消息的显示和当前用户的输入显示会有一些错位 ^_^ 

### 注册和登陆
刚进入客户端后，进入登陆注册逻辑，此时客户端提示：
```
Login or Register an account:
```
用户输入`log`或`reg`后，分别进入登陆和注册逻辑，程序会提示用户输入用户名和密码，输入用户名和密码后即可登陆和注册。

#### 注册 reg
客户端显示：
```
Login or Register an account:
reg
Register an account:
name:test
password:123
Register Successfully!
```
服务端显示：
```
user register from ('127.0.0.1', 3866)
```

用户注成功后会提示注册成功，此时可以用刚注册的账号登陆。如果用户名已经被注册过或者用户名不合法则会提示注册失败及原因。

#### 登陆 log
客户端显示
```
Login or Register an account:
log
Login the account:
name:netease1
password:123
Login in Successfully!
join to the lobby
netease1>>>
```

服务端显示
```
user ('127.0.0.1', 3866) login with name: netease1
```

用户登陆成功后即进入游戏性大厅，此时用户输入前会提示相应的用户名。

### 帮助选项 help

进入大厅后，用户可以输入相应的命令进行操作，输入`help`可以查看帮助选项：
```
netease1>>> help
help                        show help messages
chatroom   [msg]            send message to the current room.
createroom [roomname]       create a new room and enter this room
leaveroom                   leave current room
21game     [msg]            answer the 21game declared in the room
listroom                    list all the rooms in the lobby
listroomuser                list all the users in the current room
enterroom  [roomname]       leave current room and enter this room
chatall    [msg]            send message to lobby and all the other users will receive.
chatwith   [user] [msg]     send private msg to the user with user name
exit                        exit the lobby
```
第一列是相应的命令名称，第二列是需要的其他选项，例如需要发送的信息或者需要创建房间的名称等。

最后一列是该命令的说明介绍。

### 房间操作

#### 创建房间 createroom

用户输入`createroom`和相应的房间名即可创建房间，要求房间名称只能是数字、字母和下划线的组合，否则会提示用户名称输入非法。

客户端显示：
```
netease1>>> createroom ROOM1
netease1>>>
(Server) Room [ROOM1] creates successfully.
(Server) Enter room [ROOM1]
```

服务端显示：
```
[netease1] create room: [ROOM1].
```

创建房间成功后会受到服务器端的提示：房间创建成功，此时用户会自动进入房间，因为服务器会自动回收空的房间（没有用户的房间）。

#### 房间列表 listroom
用户可以输入`listroom`查看当前游戏大厅中所有的房间列表。

客户端显示：
```
netease3>>> listroom
netease3>>>
(Server) Rooms in Server:
[ROOM2],  [ROOM1],
```

服务端显示：
```
[netease3] list all rooms.
```

#### 进入房间 enterroom

用户输入`enterroom`和房间名称可以进入相应房间

客户端显示
```
netease3>>> enterroom ROOM1
netease3>>>
(Server) Enter room [ROOM1] successfully
```
服务端显示
```
[netease3] enter room: [ROOM1].
```

如果用户在进入或创建房间时已经在房间当中，则会自动退出当前房间，进入新的房间。

#### 退出房间 leaveroom

用户输入`leaveroom`可以退出当前房间。

客户端显示：
```
netease3>>> leaveroom
netease3>>>
(Server) Leave room[ROOM1] successfully
```

服务端显示:
```
[netease3] leave current room.
```

#### 列出当前房间用户 listroomuser

用户还可以使用命令`listroomuser`查看当前房间中都有哪些用户。

客户端显示：
```
netease3>>> listroomuser
netease3>>>
(Server) Users in Room[ROOM1]:
[netease1],  [netease3],
```

服务端显示
```
[netease3] list room users.
```

### 消息发送

服务器支持三种消息的发送：全局消息，房间内消息和私聊

#### 发送全局消息 chatall

客户端使用chatall命令可以发送全局消息：

客户端3：
```
netease3>>> chatall hello, netease1
netease3>>>
15:25:27 (Lobby) [netease1]: nice to meet you, netease3
```

客户端1：
```
netease1>>>
15:24:53 (Lobby) [netease3]: hello, netease1
chatall nice to meet you, netease3
netease1>>>
```

客户端2：
```
netease2>>>
15:24:53 (Lobby) [netease3]: hello, netease1

15:25:27 (Lobby) [netease1]: nice to meet you, netease3
```

服务端：
```
[netease3] send all message: [hello, netease1]
[netease1] send all message: [nice to meet you, netease3]
```
发送全局消息时，大厅内所有人除了本人都会收到该消息。

#### 发送房间内消息 chatroom

用户可以发送房间内消息，下面将用户`netease1`、`netease2`进入房间，`netease3`仍在大厅。

客户端1：
```
chatroom hello, everyone in room
netease1>>>
15:29:49 (Room: ROOM1) [netease2]: hello~
```

客户端2：
```
15:29:37 (Room: ROOM1) [netease1]: hello, everyone in room
chatroom hello~
netease2>>>
```

服务端：
```
[netease1] in room[ROOM1] send room messages [hello, everyone in room]
[netease2] in room[ROOM1] send room messages [hello~]
```

发送房间内消息时，该房间内所有人除了本人都会收到该消息。

#### 私聊 chatwith

用户可以用`chatwith`命令进行私聊，输入时要同时输入用户名称。如果用户没有登陆，服务器则提示该用户不在线上。

客户端1：
```
netease1>>> chatwith netease2 hello, netease2
netease1>>>
15:35:49 (Private) [netease2]: hi, netease1

netease1>>> chatwith haha hello
netease1>>>
(Server) User haha is not online.
```

客户端2：
```
netease2>>>
15:35:30 (Private) [netease1]: hello, netease2
chatwith netease1 hi, netease1
```

服务端：
```
[netease1] send msg to [netease2]: [hello, netease2]
[netease2] send msg to [netease1]: [hi, netease1]
[netease1] send msg to [haha]: [hello]
```

### 21点游戏

服务器中每个房间每到分钟整点（例如：00:01:00，23:59:00等）会随机生成4个1到10的数，发布在房间内，房间中的所有人可以看到。（便于测试将题目公布时间设置为了分钟整点，更改相应计时函数后即可设置为半点发布，如8点，8点半等）

留给用户的答题时间是30秒，如果有用户在30秒内输入答案并且回答正确，则服务器会在向房间内的所有人提示获胜的用户及其答案。如果没有人回答或者所有人回答不符合规则（没有用规定的数字，个数不对等），或者回答均不正确（结果大于21等），则提示没有人获胜。

#### 题目发布

用户netease1和netease2在ROOM1中，用户neteasee3在ROOM3中。

当规定时间超过后，服务器会自动提示游戏结束并公布游戏结果。


客户端1：
```
15:45:00 (Room: ROOM1) Game Problem: 10 5 1 3
15:45:30 (Room: ROOM1) Game Over!

(Room: ROOM1) Nobody Win!
```

客户端2：
```
15:45:00 (Room: ROOM1) Game Problem: 10 5 1 3
15:45:30 (Room: ROOM1) Game Over!

(Room: ROOM1) Nobody Win!
```

客户端3：
```
15:45:00 (Room: ROOM3) Game Problem: 2 7 4 3
15:45:30 (Room: ROOM3) Game Over!

(Room: ROOM3) Nobody Win!
```

服务端：
```
15:45:00 game declared in room[ROOM3]: 2 7 4 3 
15:45:00 game declared in room[ROOM1]: 10 5 1 3 
15:45:30 game over in room[ROOM3]
15:45:30 game over in room[ROOM1]
```

#### 回答问题 21game

玩家可以使用`21game`命令向服务器发送问题的答案。

问题结束后，服务器会公布获胜的玩家及其回答的答案。

客户端1：
```
netease1>>>
15:53:00 (Room: ROOM1) Game Problem: 5 8 9 10
15:53:30 (Room: ROOM1) Game Over!

(Room: ROOM1) [netease2] Win! Answer: [5 + 8 - 9 + 10]
```

客户端2：
```
netease2>>>
15:53:00 (Room: ROOM1) Game Problem: 5 8 9 10

netease2>>> 21game 5 + 8 - 9 + 10
netease2>>>
(Server) Server receive answer successfully.

15:53:30 (Room: ROOM1) Game Over!

(Room: ROOM1) [netease2] Win! Answer: [5 + 8 - 9 + 10]
```

服务端：
```
15:53:00 game declared in room[ROOM3]: 4 9 1 9 
15:53:00 game declared in room[ROOM1]: 5 8 9 10 
Receive answer from netease2 in Room ROOM1: [5 + 8 - 9 + 10]
15:53:30 game over in room[ROOM3]
15:53:30 game over in room[ROOM1]
```

#### 没有进入房间或者在非规定时间内回答问题

如果用户没有在房间中，或者用户已经退出房间，或者没有在规定时间内答题，服务器会检测相应的错误。

客户端：
```
netease3>>> 21game 1 + 1
netease3>>>
(Server) Not in any room now.

netease3>>> createroom ROOM3
netease3>>>
(Server) Room [ROOM3] creates successfully.
(Server) Enter room [ROOM3]

netease3>>> 
16:01:00 (Room: ROOM3) Game Problem: 8 3 1 9
netease3>>>
16:01:30 (Room: ROOM3) Game Over!

(Room: ROOM3) Nobody Win!

netease3>>> 21game 1 + 1
netease3>>>
(Server) It's not at answer time now.
```

服务端：
```
[netease3] create room: [ROOM3].
16:01:00 game declared in room[ROOM3]: 8 3 1 9 
16:01:30 game over in room[ROOM3]
Receive answer from netease3 in Room ROOM3: [1 + 1]
```

## 用户数据

用户的数据以文件的形式存放在服务端的`server/userdata`目录下，文件名即用户名，每个文件中以json数据格式记录用户的数据。

文件中会储存用户名（name），密码（pass），登陆总时间（timeval），上次登陆时间（last_login_time）等。登陆总时间的单位是秒。

> cur_room是指用户当前所在房间，是在内存中存放的数据，用户退出后便置为`None`，所以文件中cur_room关键字均是`None`，这里保留该数据算是偷懒了吧。

例如：

文件netease1：
```
{"cur_room": null, "timeval": 3509.475, "last_login_time": "2018-02-27 15:21:19", "name": "netease1", "pass": "123"}
```

文件neteasee2：
```
{"cur_room": null, "timeval": 3011.71, "last_login_time": "2018-02-27 15:50:39", "name": "netease2", "pass": "123"}
```

# 项目实现

## 通信消息格式

### 消息格式
整个项目的socket连接采用的是TCP连接，因为tcp是数据流的形式，所以这里需要自己定义一下服务器和客户端通信消息的形式。

消息格式定义：
```
|--len--|-----data------|
|   4   |    jsonstr    |
```
消息开头是一个4个直接的字符串，即一个int的字节的形式来储存后面data的长度，方式是通过python自带的`struct`将一个整数转化为字节形式的字符串。

其后的jsonstr是一个json形式的字符串，即需要发送的数据。

具体的发送函数：
```python
def sendMsg(self, sock, data):
    length = struct.pack('i', len(data))
    sock.send(length + data)
```
data即需要发送的json字符串，将其长度加入之后发送出去即可。

### 指令形式
code使用的所有命令常量，指令常量均存放在`Instruction.py`文件中。

上面data的长度和内容根据指令的不同也会不同，但是每个指令需要有`'inst'`值来指定指令的内容，例如：
```python
tbl = {
    Constant.INSTRUCTION: Instructions.ACK,
    Constant.FEEDBACK: Instructions.NOT_IN_ROOM
}
```
tbl是将要发送的数据，`Constant.INSTRUCTION`即是`'inst'`，用来指定该指令是哪种指令。

客户端和服务器通信指令常量：
```python
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
```

服务端成功反馈：
```python
# server success answer
REGISTER_SUCCESS = 1000
LOGIN_SUCCESS = 1001
CREATE_ROOM_SUCCESS = 1002
ENTER_ROOM_SUCCESS = 1003
LEAVE_ROOM_SUCCESS = 1004
ANSWER_SEND_SUCCESS = 1005
```

服务端异常反馈：
```python
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
```

## 服务端实现

服务端的主程序在文件`LobbyServer.py`中。

### 处理多客户端连接

服务器采用IO复用的方式来处理多个客户端的连接，服务器主循环会阻塞在select上，直到有新的连接请求或者新的消息到来。

如果触发的是监听套接字（listenfd)则说明有新的连接请求到来，则服务器在监听队列中加入该新的套接字。如果是监听队列中的其他套接字，则说明有消息从其他客户端发送来。

```python
while True:
    # use select to support multi clients
    read_set, write_set, except_set = select.select(self.read_list, self.write_list, self.except_list)
    for sock in read_set:
        if sock is listenfd:
            connfd, client_addr = sock.accept()
            print "connect from ", connfd.getpeername()
            self.read_list.append(connfd)
            self.message_buffer[sock] = ""
        else:
            try:
                data = sock.recv(1024)
            except socket.error as e:
                self.closeClient(sock)
            else:
                if data:
                    self.readData(sock, data)
                else:
                    self.closeClient(sock)
```

在调用sock.recv函数时，如果出现`socket.error`异常或者读出的结果为空，则说明客户端已经主动断开连接，此时即调用colseClinet函数来关闭客户端的连接。

### 数据维护

服务器主要通过维护这几个变量来实现游戏逻辑：
```python
self.message_buffer = {}    # data buffer
self.user_data = {}         # sock -> user data
self.user_sock = {}         # name -> sock

self.room_list = {}         # room name -> user list of this room
```

#### message_buffer
message_buffer是用来缓存socket消息的表，它的key是各个客户端的sock，value是客户端发送来的消息缓存。

因为TCP是流套接字，消息没有明显的分界。一个TCP分节可能包含不完整的消息。所以之前规定了消息格式是由一个4个字节的length开头和其后的json_str组成。所以服务器接收到客户端的消息后首先将消息添加到该用户的缓冲区中去，随后将该socket中的消息循环处理完。

```python
def readData(self, sock, data):
    if sock not in self.message_buffer.keys():
        self.message_buffer[sock] = ""
    self.message_buffer[sock] += data
    msg = self.message_buffer[sock]
    while len(msg) > 4:
        length = struct.unpack('i', data[0:4])[0]
        if len(msg) < 4 + length:
            break
        inst = msg[4:4 + length]
        self.operateInst(sock, inst)
        msg = msg[4 + length:]
    self.message_buffer[sock] = msg
```

从缓冲区中读取消息时，首先判断其长度是否大于4，如果大于4则说明已经可以读取该消息的长度。随后将length解析出来。再判断缓冲区中的剩余字符串的长度是否小于length。如果小于length，则说明数据发送不完全，则退出本次循环，否则将数据读取出来并处理。并判断缓冲区中是否仍有完整的消息。

#### user_data

user_data是用来储存用户数据的dict，即当用户成功登陆后，便将目录`server/userdata`目录下的该用户数据读取出来放入user_data中。

user_data的key是该用户连接的socket，value便是该用户的数据。

user_data会储存下该用户本次的登陆时间，当用户退出，即关闭socket时，便通过用户的登陆时间计算出用户的本次在线时间，更新到用户数据后，重新储存到文件中。

#### user_sock

user_sock主要是用来获取用户socket的，key是用户名，value则是用户的socket。

用户发送消息时是通过用户名来发送消息的，这时需要通过用户名得到该用户的socket。

#### room_list
room_list主要用来管理服务器中的房间，key是该房间的名称，value是该房间中的用户列表（socket的列表）。

当用户创建房间时，如果该房间名此时不在room_list中，则将房间名加入到room_list中并将该用户的socket加入到该房间中。

当用户进入房间时便会在该room_list中寻找房间名。

当用户退出room时便会从room_list中删除该用户，如果此时房间变为空的，则删除该房间。

用户退出房间时会调用函数：
```python
def outofRoom(self, sock, room_name):
    # leave the current room, if on one in this room, then delete this room
    if room_name and room_name in self.room_list:
        self.game_thread.outofRoom(sock, room_name)
        self.room_list[room_name].remove(sock)
        if len(self.room_list[room_name]) == 0:
            self.game_thread.deleteRoom(room_name)
            self.room_list.pop(room_name)
```
outroom会检测该房间是否需要清除。

self.game_thread是用来处理21点游戏逻辑的线程对象，当用户退出房间时也需要通知该线程对象清空该用户在该房间中的游戏数据。

### 用户退出

当检测到用户退出后，则调用closeClint函数清空该用户在服务器中的数据，并将该用户的数据储存在本地文件中。

```python
def closeClient(self, sock):
    print "socket closing", sock.getpeername()
    if sock in self.read_list:
        self.read_list.remove(sock)
    if sock in self.message_buffer.keys():
        self.message_buffer.pop(sock)
    if sock in self.user_data.keys():
        user_data = self.user_data[sock]
        user_name = user_data[Constant.NAME]
        cur_room = user_data[Constant.CURRENT_ROOM]
        user_data[Constant.CURRENT_ROOM] = None

        now_time = datetime.datetime.now()
        timeval = (now_time - user_data[Constant.LAST_LOGIN_TIME]).total_seconds()
        user_data[Constant.TIMEVAL] += timeval
        # change last login time for json dumps
        user_data[Constant.LAST_LOGIN_TIME] = user_data[Constant.LAST_LOGIN_TIME].strftime('%Y-%m-%d %H:%M:%S')

        # user leave current room

        self.outofRoom(sock, cur_room)
        self.user_data.pop(sock)
        self.user_sock.pop(user_name)

        # update user data to file
        with open(self.user_path + '\\' + user_name, 'w') as user_file:
            data_str = json.dumps(user_data)
            user_file.write(data_str)
    sock.shutdown(socket.SHUT_WR)
```

### 消息处理

服务器通过客户端发送来的消息指令的格式来调用不同的函数对笑嘻嘻进行处理。

```python
def operateInst(self, sock, inst):
    tbl = json.loads(inst)
    if Constant.INSTRUCTION in tbl.keys():
        if tbl[Constant.INSTRUCTION] == Instructions.REGISTER:
            self.userRegister(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.LOGIN:
            self.userLogin(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.SENDALL:
            self.sendALL(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.CREATE_ROOM:
            self.createRoom(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.ENTER_ROOM:
            self.enterRoom(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.LIST_ROOM:
            self.listRoom(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.LEAVE_ROOM:
            self.leaveRoom(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.SEND_ROOM:
            self.sendRoom(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.LIST_ROOM_USER:
            self.listRoomUser(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.SENDTO:
            self.sendWith(sock, tbl)
        elif tbl[Constant.INSTRUCTION] == Instructions.ANSWER:
            self.game_thread.receiveAnswer(sock, tbl)

```

### 游戏线程

之前服务器的需求知识相应客户端的应答，所以服务器阻塞在select上响应客户端的消息。21点游戏的要求时服务器定时主动向客户端发送消息，所以需要用一个单独的线程来处理游戏逻辑。

游戏的线程类在文件`GameThread.py`中，在服务端的主循环开始前调用startGame函数开始游戏线程。
```python
def startGame(self):
    self.game_start = True
    self.game_thread.start()
```

该线程类继承自threading.Thread类，需要从写run函数。

主逻辑：
```python
def run(self):
    while True:
        self.sleepToMinute()
        self.sendProblem()
        self.at_answer_time = True
        time.sleep(self.question_answer_time)

        self.gameOver()
        self.at_answer_time = False  # can't answer anymore
        self.sendGameResult()

        self.user_answer = {}
        self.already_answer = []
        self.send_problem_list = {}
```
线程的主逻辑即睡眠至相应的时间，向各个房间的客户端发送游戏题目，将游戏回答时间设置为True，随后睡眠游戏回答时间（30s），随后向各个客户端发送gameover提示，将游戏回答时间设置为false，向各个客户端公布游戏结果。随后将各个游戏内容变量清空。

#### 数据维护

该线程的数据维护主要通过一下几个变量：
```python
self.room_list = room_list
self.user_data = user_data

self.user_answer = {}
self.already_answer = []

self.at_answer_time = False
self.send_problem_list = {}
```

room_list 和 user_data是主线程中的数据的引用，在游戏线程中是只读的。 ps：好像有点线程安全的问题没有考虑。

user_answer是用来储存每个房间中每个用户的回答，key是room_name，value是用户回答的list，每个用户回答是一个dict，包含用户名，回答计算的结果，和回答的原内容。

关于回答的计算结果，每次收到用户回答时服务器会检测用户回答是否合法（即是否正确的用了服务器给出的4个数字），如果回答不合法则将结果至为-1，意味着此次回答失败。

already_answer是一个判断用户是否回答的列表，key是用户名。由于限定了每个用户只能回答一次，如果检测到用户已经回答了该问题，则忽略该用户剩下的回答。

self.at_answer_time是用来判断服务器是否仍在答题时间范围内，如果不在答题时间范围内则忽略用户的回答。

send_problem_list是服务器向哪些房间中发送了问题以及问题的内容。key是房间的名称，value是该问题的4个数字的list。这个变量主要是用来防止如果用户创建房间的时间刚好在服务器答题的时间范围内，此时房间内的玩家在本轮答题时间中是没有收到问题的，也就不用向该房间内的玩家发送游戏结果。所以在服务器发送结果时会判断之前向哪些房间中发布了问题。value是用来判断用户发送完回答后该用户的回答用的数字是否和服务器之前发布的问题中的数字一样。


## 客户端实现

由于客户端不知道服务器何时会返回消息或者发送游戏题目，故客户端同样采用多线程。

客户端主线程阻塞在用户输入上，通过用户输入的指令发送TCP消息。

客户端的子线程则专门用来监听服务端的消息并打印在终端。

由于客户端的登陆和注册逻辑是需要服务端的反馈的：是否登陆成功等。所以客户端的多线程的开启是在客户端登陆成功之后，此前客户端接收消息的逻辑仍是在主线程中维护的。

当用户进入服务大厅后，客户端子线程便阻塞在套接字上用来监听服务器端的消息，客户端的主线程便阻塞在用户输入上。

其中一个细节是，当用户从大厅退出后，回到登陆注册操作时，子线程仍然阻塞在socket上，然而此时已经需要将socket接收消息的操作返还给主线程用来判断登陆注册操作是否成功。这里采用的方法是当用户输入exit从大厅退出后，则客户端主动断开socket连接，此时子线程则会检测到socket断开而抛出socket.error异常，子线程捕获该异常后则退出，即关闭子线程。主线程在关闭套接字后则重新调用connect连接服务器。所以当在客户端输入exit后可以看到服务器端提示客户端退出后重新连接。

客户端接收消息的机制同服务端一样需要用一个buffer缓存TCP的字节流。不同的是当客户端开启接收消息的线程后需要将主线程的buffer中的内容copy到子线程中并将主线程buffer中的内容清空。