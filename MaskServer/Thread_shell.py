from pip._vendor.distlib.compat import raw_input
import threading

from MaskServer import globalVars
from MaskServer.Thread_udp import Online_udp,ListMask_udp,ListMsg_udp

class Thread_shell (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                shellStr=raw_input("ServerRoot$")
                shell=shellStr.split(" ")

                if shell[0]=="exit":
                    print("exit")
                    break

                elif shell[0]=="/dist":
                    #列出当前所有行政区，以及当前是否处于口罩预约的状态
                    with globalVars.distInfoLock:
                        for key,value in globalVars.districtInfo.items():
                            if value[0]==1:
                                condition="正在预约"
                            else:
                                condition="不在预约"
                            print("[ "+key+" ] : "+condition+" 口罩数量:"+str(value[1])+" 被预约口罩数:"+
                                  str(value[2])+" 参加预约人数:"+str(len(value[3])))

                elif shell[0]=="/distUsr":
                    print(globalVars.distUsrInfo)

                elif shell[0]=="/onlineUsr":
                    print(globalVars.onlineUsrInfo)

                elif shell[0]=="/usrUnsent":
                    print(globalVars.usrUnsentMsg)

                elif shell[0]=="/append":
                    #增加某个行政区
                    distName=shell[1]
                    print("增加"+distName+"地区")
                    with globalVars.distInfoLock:
                        globalVars.districtInfo[distName]=[0,0,0,set()]

                elif shell[0]=="/erase":
                    #删除某个地区
                    with globalVars.distInfoLock:
                        del globalVars.districtInfo[shell[1]]

                elif shell[0]=="/enter":
                    #进入某个行政区
                    self.mamageDistricts(shell[1])

                elif shell[0]=="/msg":
                    args=shell[1:-1]
                    argsSet=set()
                    msg=shell[-1]
                    i=0
                    while i<len(args)-1:
                        argsSet.add((args[i],args[i+1]))
                        i+=2

                    with globalVars.onlineUserLock and globalVars.usrUnsentLock:
                        onlineUsr=set(list(globalVars.onlineUsrInfo.keys()))-argsSet
                        offlineUsr=argsSet-onlineUsr

                        for each in offlineUsr:
                            if each in globalVars.usrUnsentMsg.keys():
                                globalVars.usrUnsentMsg[each].append(msg)
                            else:
                                globalVars.usrUnsentMsg[each]=([msg])

                    listUdp=ListMsg_udp(msg,onlineUsr)
                    listUdp.start()

                else:
                    print(shellStr+" is not a commond")

            except:
                print("unexpected commond error!")

    def mamageDistricts(self,districtName):
        while True:
            shellStr=raw_input("ServerRoot/"+districtName+"$")
            shell=shellStr.split(" ")

            if shell[0]=="/leave":
                break

            elif shell[0]=="/openNewround":
                #开通新一轮口罩预约并设置口罩数量
                with globalVars.distInfoLock:
                    if globalVars.districtInfo[districtName][0]==0:
                        globalVars.districtInfo[districtName][0]=1
                        globalVars.districtInfo[districtName][1]=int(shell[1])

                        with globalVars.distUsrLock:
                            distInfo=globalVars.distUsrInfo.values()
                            for each in distInfo:
                                each[2]=0

                        print("开放新一轮预约成功,本次预约口罩数:"+shell[1])

                    else:
                        print(districtName+"已在预约中")

            elif shell[0]=="/list":
                #列出当前行政区的预约情况
                with globalVars.distInfoLock:
                    value=globalVars.districtInfo[districtName]
                    if value[0] == 1:
                        condition = "正在预约"
                    else:
                        condition = "不在预约"
                    print("[ " + districtName + " ] : " + condition + " 口罩数量:" + str(value[1]) + " 被预约口罩数:" +
                          str(value[2]) + " 参加预约者:" + str(value[3]))

            elif shell[0]=="/kickout":
                #踢出预约者并广播
                usrName=shell[1]
                onlineUdp = Online_udp("[ 系统消息 ] 踢出预约用户:" + usrName)
                onlineUdp.start()

                with globalVars.onlineUserLock:
                    if (districtName,usrName) in globalVars.onlineUsrInfo.keys():
                        del globalVars.onlineUsrInfo[(districtName,usrName)]
                with globalVars.distInfoLock:
                    if usrName in globalVars.districtInfo[districtName][3]:
                        globalVars.districtInfo[districtName][3].remove(usrName)

            elif shell[0]=="/ban":
                #禁封账号并广播
                usrName=shell[1]
                onlineUdp = Online_udp("[ 系统消息 ] 禁封用户:" + usrName)
                onlineUdp.start()

                with globalVars.distUsrLock:
                    if usrName in globalVars.distUsrInfo[districtName].keys():
                        del globalVars.distUsrInfo[districtName][usrName]

            elif shell[0]=="/handout":
                #分发口罩结束本轮预约并广播
                with globalVars.distInfoLock:
                    if globalVars.districtInfo[districtName][0]==1 and len(globalVars.districtInfo[districtName][3])>0:
                        with globalVars.distUsrLock:
                            for key, value in globalVars.distUsrInfo[districtName].items():
                                value[1] = 0

                        globalVars.districtInfo[districtName][0]=0
                        globalVars.districtInfo[districtName][1]-=globalVars.districtInfo[districtName][2]
                        globalVars.districtInfo[districtName][2]=0

                        usrSet=globalVars.districtInfo[districtName][3]
                        usrAddrList=[]
                        for each in usrSet:
                            usrAddrList.append((districtName,each))

                        listMaskUdp=ListMask_udp(usrAddrList)
                        listMaskUdp.start()

                        globalVars.districtInfo[districtName][3]=set()

                        print("发放口罩成功")

                    else:
                        print("发放口罩失败")

            else:
                print(shellStr+" is not a commond")