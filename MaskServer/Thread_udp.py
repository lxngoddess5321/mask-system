import json
import socket
import threading
import random

from MaskServer import globalVars

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 10000))

class Thread_udp (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                clientData,clientAddr=sock.recvfrom(1024)
                udpThread=Udp_connection(json.loads(clientData.decode("utf-8")),clientAddr)
                udpThread.start()
            except:
                print("udp connect error!")

class Udp_connection (threading.Thread):
    def __init__(self,data,addr):
        threading.Thread.__init__(self)
        self.data=data
        self.addr=addr

    def run(self):
        try:
            #与单个客户端的连接
            #print("from ",self.addr," : ",self.data)
            dist=self.data['dist']
            usrName=self.data['usrName']
            operation=self.data['operation']

            with globalVars.onlineUserLock:
                if (dist,usrName) in globalVars.onlineUsrInfo.keys():
                    signCon=1
                else:
                    signCon=0

            if signCon==0:#用户未登录
                if operation==0: #"signUp"
                    #用户注册
                    with globalVars.distUsrLock:
                        globalVars.distUsrInfo[dist][usrName]=[self.data['usrId'],0]

                    opInfo=1 #"注册成功"

                elif operation==1: #"signIn"
                    #用户登陆
                    with globalVars.distUsrLock:
                        if dist in globalVars.distUsrInfo.keys() and usrName in globalVars.distUsrInfo[dist]:
                            if self.data['usrId']==globalVars.distUsrInfo[dist][usrName][0]:
                                    with globalVars.onlineUserLock and globalVars.usrUnsentLock:
                                        globalVars.onlineUsrInfo[(dist,usrName)]=self.addr
                                        if (dist,usrName) in globalVars.usrUnsentMsg.keys():
                                            opInfo = 0 #返回消息
                                            retData = {"opInfo": opInfo, "msg": globalVars.usrUnsentMsg[(dist,usrName)]}
                                            del globalVars.usrUnsentMsg[(dist,usrName)]
                                        else:
                                            opInfo = 2  # "登陆成功"

                            else:
                                opInfo=3 #"密码错误"
                        else:
                            opInfo=4 #"用户未注册"
                else:
                    opInfo=5 #用户未登录

            else: #用户已登陆
                if operation==2: #"logOut"
                    opInfo=6 #用户退出登录
                    with globalVars.onlineUserLock:
                        del globalVars.onlineUsrInfo[(dist,usrName)]

                elif operation==3: #"districts"
                    opInfo=0 #返回信息
                    msgList = []
                    with globalVars.distInfoLock:
                        for key, value in globalVars.districtInfo.items():
                            msgList.append((key,value[0]))

                    retData={"opInfo": opInfo, "msgList": msgList}

                elif operation==4: #"list distrctName"
                    with globalVars.distInfoLock:
                        serchDist = self.data['serchDist']
                        if serchDist not in globalVars.districtInfo.keys():
                            opInfo=9 #地区不存在
                        else:
                            opInfo = 0  # 返回信息
                            if globalVars.districtInfo[serchDist][0]==1:
                                msg=[1,globalVars.districtInfo[serchDist][1],
                                     globalVars.districtInfo[serchDist][2],
                                     len(globalVars.districtInfo[serchDist][3])]
                            else:
                                msg=[0]
                            retData={"opInfo": opInfo, "distMsg": msg}

                elif operation==5: #"join districtName  maskNum"
                    with globalVars.distInfoLock:
                        if dist not in globalVars.districtInfo.keys():
                            opInfo=9 #地区不存在
                        else:
                            distInfo = globalVars.districtInfo[dist]
                            if distInfo[0]==1 and self.data['bookNum']+distInfo[2]<=distInfo[1]:
                                opInfo = 7  # 预定口罩成功
                                distInfo[3].add(usrName)
                                distInfo[2]+=self.data['bookNum']
                                with globalVars.distUsrLock:
                                    globalVars.distUsrInfo[dist][usrName][1]+=self.data['bookNum']

                                onlineUdp=Online_udp("[ 系统消息 ] : 用户 "+usrName+" 成功预定了"+str(self.data['bookNum'])+"个口罩")
                                onlineUdp.start()

                            elif  self.data['bookNum']+distInfo[2]>distInfo[1] :
                                print("[ "+dist+ " ] : "+"口罩预约已满,请尽快发放")

                            else:
                                opInfo = 8  # 当前不开放预约或口罩已分配完

                else:
                    opInfo=10 #操作错误

            if opInfo!=0:
                retData={"opInfo": opInfo}

            sock.sendto(json.dumps(retData,ensure_ascii=False).encode('utf-8'), self.addr)

        except:
            print("udp error!")

class Online_udp (threading.Thread):
    def __init__(self, msg):
        threading.Thread.__init__(self)
        self.msg=msg
        self.onlineSock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def run(self):
        with globalVars.onlineUserLock:
            try:
                for key,value in globalVars.onlineUsrInfo.items():
                    data={'opInfo':12,"msg":self.msg} #表示消息
                    self.onlineSock.sendto(json.dumps(data,ensure_ascii=False).encode('utf-8'),value)

                self.onlineSock.close()
            except:
                print("unexpected udp error!")

class ListMask_udp (threading.Thread):
    def __init__(self, addrList):
        threading.Thread.__init__(self)
        self.addrList=addrList #[("dist","usrName"), ...]
        self.listSock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def run(self):
        try:
            num=len(self.addrList)
            left=num*1000
            right=num*10000
            for each in self.addrList:
                with globalVars.onlineUserLock:
                    if each in globalVars.onlineUsrInfo.keys():
                        data={'opInfo':11,"pickCode":random.randint(left,right)} #11表示口罩下发
                        self.listSock.sendto(json.dumps(data,ensure_ascii=False).encode('utf-8'),globalVars.onlineUsrInfo[each])

                    else:
                        with globalVars.usrUnsentLock:
                            if each in globalVars.usrUnsentMsg.keys():
                                globalVars.usrUnsentMsg[each].append({'opInfo':11,"pickCode":random.randint(left,right)})#11表示口罩下发
                            else:
                                globalVars.usrUnsentMsg[each]=([{'opInfo':11,"pickCode":random.randint(left,right)}])#11表示口罩下发

            self.listSock.close()
        except:
            print("unexpected mask udp error!")


class ListMsg_udp(threading.Thread):
    def __init__(self, msg, addrList):
        threading.Thread.__init__(self)
        self.msg = msg
        self.addrList = addrList  # [("dist","usrName"), ...]
        self.listSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        try:
            for each in self.addrList:
                with globalVars.onlineUserLock:
                    if each in globalVars.onlineUsrInfo.keys():
                        data = {'opInfo': 0, "msg": self.msg}  # 返回消息
                        self.listSock.sendto(json.dumps(data, ensure_ascii=False).encode('utf-8'),
                                             globalVars.onlineUsrInfo[each])

                    else:
                        with globalVars.usrUnsentLock:
                            globalVars.usrUnsentMsg[each].append({'opInfo': 12, "msg": self.msg})# 表示列表发送消息

            self.listSock.close()
        except:
            print("unexpected list msg udp error!")





