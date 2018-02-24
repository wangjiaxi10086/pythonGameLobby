import struct
import json
import os

if __name__ == '__main__':
    a = 20
    s = struct.pack('i', a)
    print repr(s)
    result = struct.unpack('i', s)
    print result[0]

    cla = { "name": "netease1", "pass": "123"}
    cla_str = json.dumps(cla)
    print cla_str

    cla = json.loads(cla_str)
    print cla

    print os.getcwd()
    print os.listdir(os.getcwd() + "\\server")

    with open('asdf', 'w') as f:
        pass