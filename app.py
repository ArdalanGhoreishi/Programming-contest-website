from flask import Flask, flash, redirect, render_template, \
     request, url_for
import numpy as np
import pandas_zmq as pz
import pandas as pd
import datetime as dt
from werkzeug.utils import secure_filename
import os
from math import *
import zmq
import json
PEOPLE_FOLDER = os.path.join('static')

app = Flask(__name__)

def saveList(myList,filename):
    # the filename should mention the extension 'npy'
    np.save(filename,myList)
    print("Saved successfully!")
def loadList(filename):
    # the filename should mention the extension 'npy'
    tempNumpyArray=np.load(filename, allow_pickle=True)
    return tempNumpyArray.tolist()
Cnamelist=[['C1','2022-2-27 20:40:00','سوال اول ضرب و سوال دوم توان']]
saveList(Cnamelist,'Cnamelist.npy')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
@app.route('/')
def index():
    return render_template(
        'index.html',
        data=[{'name':'admin'}, {'name':'contestant'}])

@app.route("/" , methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        if request.form['comp_select'] == 'admin':
            return redirect(url_for('login'))
        else:
            return redirect(url_for('contestant'))
    else:
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
                request.form['password'] != 'admin':
            error = 'Invalid username or password. Please try again!'
        else:
            return redirect(url_for('regcontest'))
    return render_template('login.html', error=error)
@app.route('/contestant')

def contestant():
    contestt = loadList('Cnamelist.npy')
    j=0
    size=len(contestt)
    i=0
    while i<size:
        if dt.datetime.strptime(contestt[j][1],'%Y-%m-%d %H:%M:%S')<dt.datetime.now():
            contestt.pop(j)
            j=j-1
        j=j+1
        i=i+1
    df=pd.DataFrame (contestt,columns=['contest name','Deadline','توضیحات'])
    contests=[]
    for i in range(0,len(contestt)):
        contests.append(contestt[i][0])
    return render_template('contestant.html',contests=contests,data=df.to_html())


def upload_file():
    return render_template('contestant.html')


@app.route('/contestant/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        code = f.read()
        code = code.decode('utf-8')
        contest = request.form.get("contestDropdown")
        sender = request.form.get("sender")
        datetime=dt.datetime.now()
        datetime=str(datetime)
        work = dict(
            sender=sender,
            datetime=datetime,
            code=code,
            contest=contest,
        )
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        connection = "tcp://localhost:1000"
        socket.connect(connection)
        socket.send_json(work)
        resultss=pz.recv_dataframe(socket)
        print(resultss)
        f.save(secure_filename(f.filename))
        return resultss.to_html(header="true", table_id="table")
@app.route('/regcontest')
def regcontest():
   full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'formsample.png')
   return render_template('regcontest.html' , user_image = full_filename)

@app.route('/regcontestdone',methods = ['POST', 'GET'])
def regcontestdone():
   if request.method == 'POST':
      Cnamelist = loadList('Cnamelist.npy')
      file=request.files['file']
      file = file.read()
      file = file.decode('utf-8')
      spl=file.split('\n')
      CName=spl[0].rstrip()
      E111=spl[1]
      E112=spl[2]
      E121=spl[3]
      E122=spl[4]
      O11=spl[5]
      O12=spl[6]
      E211=spl[7]
      E212=spl[8]
      E221=spl[9]
      E222=spl[10]
      O21=spl[11]
      O22=spl[12]
      description=spl[13].rstrip()
      deadline=spl[14].rstrip()
      Cnamelist.append([CName,deadline,description])
      saveList(Cnamelist,'Cnamelist.npy')

      reg = dict(
          sender='admin',
          CName=CName,
          E111=int(E111),
          E112=int(E112),
          E121=int(E121),
          E122=int(E122),
          O11=int(O11),
          O12=int(O12),
          E211=int(E211),
          E212=int(E212),
          E221=int(E221),
          E222=int(E222),
          O21=int(O21),
          O22=int(O22),
      )
      context = zmq.Context()
      socket = context.socket(zmq.REQ)
      connection = "tcp://localhost:1000"
      socket.connect(connection)
      socket.send_json(reg)
      message = socket.recv_json()
      print (message)
      return 'register is done'
@app.route('/showresult')

def showresult():
    contestt = loadList('Cnamelist.npy')
    df = pd.DataFrame(contestt, columns=['contest name', 'Deadline', 'توضیحات'])
    contests = []
    for i in range(0, len(contestt)):
        contests.append(contestt[i][0])
    return render_template('showresult.html',contests=contests,data=df.to_html())


def select_contest():
    return render_template('contestant.html')


@app.route('/showresult/select_contest', methods=['GET', 'POST'])
def select_contest():
    if request.method == 'POST':
        contest = request.form.get("contestDropdown")
        sender = "User"
        work = dict(
            sender=sender,
            contest=contest,
        )
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        connection = "tcp://localhost:1000"
        socket.connect(connection)
        socket.send_json(work)
        resultss=pz.recv_dataframe(socket)
        print(resultss)
        return resultss.to_html(header="true", table_id="table")
if __name__=='__main__':
    app.run(debug=True)