import threading

#在线用户
#格式为{("dist","usrName"):("addr",port), ...}
onlineUsrInfo={}
onlineUserLock=threading.Lock()

#地区信息
#格式为{"地区名":[0(是否在预约)，0(口罩数量), 0(已被预约数量), {}(参加预约人集合)], ...}
#为了方便测试,我们预存一些地区信息
districtInfo={
    "北京":[1,10,8,{"张三","李四","王五"}]
}
distInfoLock=threading.Lock()

#各地区用户信息
#格式为{"dist"：{"usrName":[usrId,0(预约数量),00000(用户取口罩码)], ...}， ...}
#取口罩码在开始分发后加入,下一轮开始后作废删除
#为了方便测试,我们预存一些用户账号
distUsrInfo={
    "北京":{
        "张三":["123",2],
        "李四":["1234",3],
        "王五":["12345",3]
    }
}
distUsrLock=threading.Lock()

#用户未接收的消息
#格式为{("dist","usrName"):["msg",...], ...}
usrUnsentMsg={}
usrUnsentLock=threading.Lock()