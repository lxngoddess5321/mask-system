import threading

#全局消息变量
msgList=[]
msgLock=threading.Lock()

feedBackMsg=[]
feedBackLock=threading.Lock()