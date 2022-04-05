import threading
import time
import zmq
import json
import pandas_zmq as pz
import numpy as np
import pandas as pd
import JudgeWorker
t=0
contestlist=[["C1" , 2 , 3, 4 , 3, 6, 12 ,2 , 3, 4 , 3, 8, 64]]
result=[]
print ('Ready to go')
def saveList(myList,filename):
    # the filename should mention the extension 'npy'
    np.save(filename,myList)
def loadList(filename):
    # the filename should mention the extension 'npy'
    tempNumpyArray=np.load(filename)
    return tempNumpyArray.tolist()
#portlist=[['5555',0]]
#saveList(portlist,'portlist.npy')
def aWorker_asRoutine( aWorker_URL, t,aContext = None ):
    """Worker routine"""
    #Context to get inherited or create a new one trick------------------------------
    aContext = aContext or zmq.Context.instance()

    # Socket to talk to dispatcher --------------------------------------------------
    socket = aContext.socket( zmq.REP )

    socket.connect( aWorker_URL )

    while True:
        work = socket.recv_json()
        if work['sender']== 'admin':
            contestlist.append([work['CName'],work['E111'],work["E112"],work["E121"],work["E122"],work["O11"],work["O12"],work['E211'],work["E212"],work["E221"],work["E222"],work["O21"],work["O22"]])
            print(contestlist)
            socket.send_json('done')
        elif work["sender"]== 'User':
            resulttable = []
            for i in range(len(result)):
                if result[i][0] == work['contest']:
                    resulttable.append([result[i][1], result[i][2], result[i][3], result[i][4]])
            restable = pd.DataFrame(resulttable, columns=['name', 'date time', 'score', 'status'])
            restable.sort_values(by=['score'], inplace=True, ascending=False)
            pz.send_dataframe(socket, restable, secret='', alg='sha256', flags=0)
        else:
            for i in range(len(contestlist)):
                if contestlist[i][0] == work['contest']:
                    E111=contestlist[i][1]
                    E112=contestlist[i][2]
                    E121=contestlist[i][3]
                    E122=contestlist[i][4]
                    O11=contestlist[i][5]
                    O12=contestlist[i][6]
                    E211 = contestlist[i][7]
                    E212 = contestlist[i][8]
                    E221 = contestlist[i][9]
                    E222 = contestlist[i][10]
                    O21 = contestlist[i][11]
                    O22 = contestlist[i][12]
                    break
            count = 0
            for i in range(len(portlist)):
                if portlist[i][1] == '0':
                    portlist[i][1] = '1'
                    Port = portlist[i][0]
                    count = 1
                    break
            if count == 0:
                Port = str(int(portlist[len(portlist) - 1][0]) + 1)
                portlist.append([Port, 1])
            nwork = dict (
                code=work["code"],
                E111=E111,
                E112=E112,
                E121=E121,
                E122=E122,
                O11=O11,
                O12=O12,
                E211=E211,
                E212=E212,
                E221=E221,
                E222=E222,
                O21=O21,
                O22=O22,
            )
            connection = "tcp://localhost:" + Port
            contexts[t] = zmq.Context()
            sockets[t] = contexts[t].socket(zmq.REQ)
            sockets[t].connect(connection)
            sockets[t].send_json(nwork)
            JudgeWorker.worker(Port)
            messages[t] = sockets[t].recv()
            messages[t] = int (messages[t])
            saveList(portlist, 'portlist.npy')
            if int(messages[t])==100:
                temp ='accepted'
            else:
                temp = 'denied'
            result.append([work['contest'], work['sender'], work['datetime'], messages[t] , temp])
            resulttable = []
            for i in range(len(result)):
                if result[i][0] == work['contest']:
                    resulttable.append([result[i][1], result[i][2], result[i][3] , result[i][4]])
            restable = pd.DataFrame(resulttable, columns=['name', 'date time', 'score', 'status'])
            restable.sort_values(by=['score'], inplace=True, ascending=False)
            pz.send_dataframe(socket , restable , secret='', alg='sha256', flags=0)

            time.sleep(3)
            for i in range(len(portlist)):
                if portlist[i][0] == Port:
                    portlist[i][1] = '0'
                    saveList(portlist, 'portlist.npy')
                    break

def main(t):
    """Server routine"""

    url_worker = "inproc://workers"
    url_client = "tcp://*:1000"

    # Prepare our context and sockets ------------------------------------------------
    aLocalhostCentralContext = zmq.Context.instance()

    # Socket to talk to clients ------------------------------------------------------
    clients = aLocalhostCentralContext.socket( zmq.ROUTER )
    clients.bind( url_client )

    # Socket to talk to workers ------------------------------------------------------
    workers = aLocalhostCentralContext.socket( zmq.DEALER )
    workers.bind( url_worker )

    # Launch pool of worker threads --------------< or spin-off by one in OnDemandMODE >
    for i in range(10):
        t=t+1
        thread = threading.Thread( target = aWorker_asRoutine, args = ( url_worker,t , ) )
        thread.start()

    zmq.device( zmq.QUEUE, clients, workers )

    # clean up
    clients.close()
    workers.close()
    aLocalhostCentralContext.term()

if __name__ == "__main__":
    sockets={}
    contexts={}
    messages={}
    portlist = loadList('portlist.npy')
    main(t)
