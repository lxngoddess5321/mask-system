from tkinter import messagebox

from MaskClient.Client_udp import Client_udp
from MaskClient.Client_udp import Recieve_msg
from MaskClient.Gui_client import *

class Client_main:
    def __init__(self,):
        self.root = Tk()
        self.root.title('口罩预约系统')
        self.loginPage=LoginPage(self.root)
        self.name=""
        self.dist=""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def run(self):
        recieveMsg=Recieve_msg()
        recieveMsg.start()
        self.root.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("提示", "是否退出"):
            clientUdp = Client_udp(self.name, None, self.dist, 2, None)
            data = clientUdp.run()
            if data['opInfo'] == 6:
                self.root.destroy()

if __name__=="__main__":
    maskClient=Client_main()
    maskClient.run()

