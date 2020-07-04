from tkinter import *
from tkinter import messagebox
from tkinter.messagebox import *

from MaskClient.Client_udp import *
from MaskClient.globalVar import *

class LoginPage(object):
    def __init__(self, master=None):
        self.root = master  # 定义内部变量root
        self.root.geometry('%dx%d' % (300, 220))  # 设置窗口大小
        self.district = StringVar()
        self.username = StringVar()
        self.password = StringVar()
        self.dist=""
        self.name=""
        self.pwd=""
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)  # 创建Frame
        self.page.pack()
        Label(self.page).grid(row=0, stick=W)
        Label(self.page, text='地区: ').grid(row=1, stick=W, pady=10)
        Entry(self.page, textvariable=self.district).grid(row=1, column=1, stick=E)
        Label(self.page, text='账号: ').grid(row=2, stick=W, pady=10)
        Entry(self.page, textvariable=self.username).grid(row=2, column=1, stick=E)
        Label(self.page, text='密码: ').grid(row=3, stick=W, pady=10)
        Entry(self.page, textvariable=self.password, show='*').grid(row=3, column=1, stick=E)
        Button(self.page, text='注册', command=self.signUp).grid(row=4, stick=W, pady=10)
        Button(self.page, text='登陆', command=self.signIn).grid(row=4, column=1, stick=E)

    def signUp(self):
        dist = self.district.get()
        name = self.username.get()
        pwd = self.password.get()

        if dist=="" or name=="" or pwd=="":
            showinfo(title='错误', message='地区名,账号或密码不能为空！')
            return

        clientUdp=Client_udp(name,pwd,dist,0,None)
        data=clientUdp.run()
        if data['opInfo']==1:
            showinfo(title='注册成功', message='请重新输入账号密码登陆！')

    def signIn(self):
        self.dist = self.district.get()
        self.name = self.username.get()
        self.pwd = self.password.get()
        clientUdp=Client_udp(self.name,self.pwd,self.dist,1,None)
        data=clientUdp.run()
        opInfo=data['opInfo']
        if opInfo==2: #登陆成功
            self.page.destroy()
            MainPage(self.root,self.dist,self.name)
        elif opInfo==3:
            showinfo(title='错误', message='密码错误！')
        elif opInfo==4:
            showinfo(title='错误', message='账号不存在，请先注册！')


class MainPage(object):

    def __init__(self, master=None, dist="", name=""):
        self.root = master  # 定义内部变量root
        self.root.geometry('%dx%d' % (400, 300))  # 设置窗口大小
        self.dist = dist
        self.name = name
        self.createPage()

    def createPage(self):
        self.msgPage = msgFrame(self.root)
        self.bookPage = bookFrame(self.root, self.dist, self.name)
        self.homePage = homeFrame(self.root, self.dist, self.name)  # 创建不同Frame
        # self.settingPage = settingFrame(self.root, self.dist, self.name, self.msgPage,self.homePage,self.bookPage)
        self.homePage.pack()  # 默认显示数据录入界面
        menubar = Menu(self.root)
        menubar.add_command(label='主页', command=self.home)
        menubar.add_command(label='参加预定', command=self.book)
        menubar.add_command(label="消息",command=self.msg)
        # menubar.add_command(label="设置",command=self.setting)
        self.root['menu'] = menubar  # 设置菜单栏

    def home(self):
        self.homePage.pack()
        self.bookPage.pack_forget()
        # self.settingPage.pack_forget()
        self.msgPage.pack_forget()

    def book(self):
        self.homePage.pack_forget()
        self.bookPage.pack()
        # self.settingPage.pack_forget()
        self.msgPage.pack_forget()

    def msg(self):
        self.homePage.pack_forget()
        self.bookPage.pack_forget()
        self.msgPage.pack()
        # self.settingPage.pack_forget()

    # def setting(self):
        # self.homePage.pack_forget()
        # self.bookPage.pack_forget()
        # self.settingPage.pack()
        # self.msgPage.pack_forget()

    # def logout(self):
    #     self.page.destroy()
    #     LoginPage(self.root)


class homeFrame(Frame):  # 继承Frame类
    def __init__(self, master=None, dist="" , name=""):
        Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.serchDist = StringVar()
        self.dist = dist
        self.name = name
        self.createPage()
        self.labs=[]

    def createPage(self):
        Label(self).grid(row=0,pady=10)
        Label(self, text='查询地区: ').grid(row=1, stick=W, pady=10)
        Entry(self, textvariable=self.serchDist).grid(row=1, column=2, pady=10)
        Button(self, text='查询', command=self.serch).grid(row=1,column=3, pady=10)

    def serch(self):
        for each in self.labs:
            each.destroy()

        arg=self.serchDist.get()

        if arg=="":
            clientUdp = Client_udp(self.name, None, self.dist, 3, None)
            data = clientUdp.run()
            if data['opInfo'] == 0 and "msgList" in data.keys():
                msgList = data['msgList']
                i = 2
                for each in msgList:
                    if each[1] == 1:
                        lb=Label(self, text=each[0] + " : 正在预约")
                        lb.grid(row=i, column=2, pady=10)
                    if each[1] == 0:
                        lb=Label(self, text=each[0] + " : 不在预约")
                        lb.grid(row=i, column=2, pady=10)
                    i += 1
                    self.labs.append(lb)

            else:
                showinfo(title='系统消息', message="地区信息错误:" + str(data['opInfo']))

        else:
            clientUdp=Client_udp(self.name,None,self.dist,4,arg)
            data=clientUdp.run()
            if data['opInfo']==0 and "distMsg" in data.keys():
                msg=data['distMsg']
                if msg[0]==1:
                    lb=Label(self,text=arg+" : 正在预约")
                    lb.grid(row=2, column=2, pady=10)
                    self.labs.append(lb)
                    lb=Label(self,text="口罩预约情况："+str(msg[2])+"/"+str(msg[1])+" 预定人数:"+str(msg[3]))
                    lb.grid(row=3, column=2, pady=10)
                    self.labs.append(lb)

                elif msg[0] == 0:
                    lb=Label(self,text=arg+" : 不在预约")
                    lb.grid(row=2, column=2, pady=10)
                    self.labs.append(lb)
            else:
                showinfo(title='系统消息', message="地区不存在")


class bookFrame(Frame):  # 继承Frame类
    def __init__(self, master=None, dist="" , name=""):
        Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.bookNum = StringVar()
        self.dist=dist
        self.name=name
        self.createPage()

    def createPage(self):
        Label(self).grid(row=0, stick=W, pady=10)
        Label(self, text='口罩数量: ').grid(row=2, stick=W, pady=10)
        Entry(self, textvariable=self.bookNum).grid(row=2, column=1, stick=E)
        Button(self, text='确认预定',command=self.book).grid(row=3, column=1, stick=E, pady=10)

    def book(self):
        bookNum=self.bookNum.get()
        if bookNum=="" or int(bookNum)<=0:
            showinfo(title='错误', message='预定数量不能为'+bookNum)
            return

        clientUdp=Client_udp(self.name,None,self.dist,5,arg=int(bookNum))
        data=clientUdp.run()
        opInfo=data['opInfo']

        if opInfo==9:
            showinfo(title='系统消息', message='所在地区未参与口罩预定')
        elif opInfo==8:
            showinfo(title='系统消息', message='所在地区不开放预约或口罩已分配完')
        elif opInfo==7:
            showinfo(title='系统消息', message='预定成功,请耐心等待口罩配发')
        else:
            showinfo(title='系统消息', message='未知的错误'+str(opInfo))

class msgFrame(Frame):  # 继承Frame类
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.labs=[]
        self.createPage()

    def createPage(self):
        self.page = Frame(self.root)  # 创建Frame
        self.page.pack()

        Label(self, text='最新消息').grid(row=1, pady=10)
        Button(self, text='刷新',command=self.refreshMsg).grid(row=2, pady=10)


    def refreshMsg(self):
        # for each in self.labs:
        #     each.destroy()
        with msgLock:
            i=3
            # print(msgList)

            for each in msgList:
                if each['opInfo']==12:
                    lb=Label(self,text=str(each['msg']))
                    lb.grid(row=i, pady=10)
                elif each['opInfo']==11:
                    lb=Label(self,text="口罩已配发,取件码为"+str(each['pickCode']))
                    lb.grid(row=i, pady=10)
                i+=1
                self.labs.append(lb)

        msgList.clear()

#self.msgPage,self.settingPage,self.homePage,self.bookPage
#, msgPage=None, settingPage=None, homePage=None, bookPage=None
# class settingFrame(Frame):  # 继承Frame类
#     def __init__(self, master=None, dist="" , name="", msgPage=None, homePage=None, bookPage=None):
#         Frame.__init__(self, master)
#         self.root = master  # 定义内部变量root
#         self.dist=dist
#         self.name=name
#         # self.settingPage=settingPage
#         self.msgPage=msgPage
#         self.homePage=homePage
#         self.bookPage=bookPage
#         self.createPage()
#
#     def createPage(self):
#         self.page = Frame(self.root)  # 创建Frame
#         self.page.pack()
#         self.bt=Button(self, text='退出登陆',command=self.destroy)
#         self.bt.grid(pady=10)
#
#     def logout(self):
#         clientUdp=Client_udp(self.name,None,self.dist,2,None)
#         data=clientUdp.run()
#
#         if data['opInfo'] == 6:
#             self.homePage.destroy()
#             self.bookPage.destroy()
#             self.msgPage.destroy()
#             self.page.destroy()
#             self.destroy()
#             LoginPage(self.root)
#
#         else:
#             showinfo(title="错误",message="退出登录失败:"+str(data['opInfo']))





