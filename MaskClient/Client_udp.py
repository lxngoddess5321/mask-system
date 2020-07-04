import json
import socket
import threading
from time import *

from MaskClient.globalVar import *

serverAddr='127.0.0.1'
serverPort=10000
sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 10001))
sockLock=threading.Lock()

class Client_udp :
    def __init__(self,name,passward,dist,option,arg):
        self.name=name
        self.passward=passward
        self.dist=dist
        self.option=option
        self.arg=arg

    def run(self):
        if self.option==0 or self.option==1: #登陆或注册
            data={'operation': self.option,'dist': self.dist,'usrName':self.name,'usrId': self.passward}

        elif self.option==2 or self.option==3: #退出登陆或查询所有地区情况
            data={'operation': self.option,'dist': self.dist,'usrName':self.name}

        elif self.option==4: #查询某地情况
            data={'operation': self.option,'dist': self.dist,'usrName':self.name,"serchDist":self.arg}

        elif self.option==5: #预定某数量的口罩
            data={'operation': self.option,'dist': self.dist,'usrName':self.name,"bookNum":self.arg}

        dataJson = json.dumps(data,ensure_ascii=False)
        sock.sendto(dataJson.encode('utf-8'), (serverAddr, serverPort))

        # print(dataJson)
        while len(feedBackMsg)==0:
            sleep(0.1)
        data=feedBackMsg[0]
        feedBackMsg.clear()
        return data


class Recieve_msg (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            data=json.loads(sock.recv(1024).decode('utf-8'))
            if data['opInfo']==12 or data['opInfo']==11:
                # with msgLock:
                print(data)
                msgList.append(data)
            else:
                feedBackMsg.append(data)
