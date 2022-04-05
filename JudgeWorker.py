import zmq
import time
import json
from math import *
def worker(Port):
    e1=5
    print('Starting worker on Port: ', Port)
    con = "tcp://*:" + Port
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(con)
    #  Wait for next request from client
    message = socket.recv_json()
    temp_dict = {}
    score = 0
    exec (message["code"],{'e11':message["E111"], 'e12' : message["E112"] , 'e21':message["E211"], 'e22':message["E212"], 'temp_dict':temp_dict})
    if temp_dict['ans1']==message['O11'] :
        score= score+1
    if temp_dict['ans2']==message['O21'] :
        score= score+1
    exec (message["code"],{'e11':message["E121"], 'e12' : message["E122"] , 'e21':message["E221"], 'e22':message["E222"], 'temp_dict':temp_dict})
    if temp_dict["ans1"]==message['O12'] :
        score= score+1
    if temp_dict["ans2"]==message['O22'] :
        score= score+1
    score=score*25
    socket.send_json(score)
    return 0



