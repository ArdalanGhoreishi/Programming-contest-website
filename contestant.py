import zmq
import json
import time
import datetime as dt
import pandas_zmq as pz

code = open("TestCodeContestant/test1.py", 'r')
code = code.read()
contest= "C1"
datetime=dt.datetime.now()
work = dict(
            sender='user',
            datetime=str(datetime),
            code=code,
            contest=contest,
        )
context = zmq.Context()
socket = context.socket(zmq.REQ)
connection = "tcp://localhost:1000"
socket.connect(connection)
for i in range (1,10):
    socket.send_json (work)
    resultss = pz.recv_dataframe(socket)
    print(resultss)
