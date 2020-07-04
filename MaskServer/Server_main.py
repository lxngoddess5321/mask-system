import threading

import MaskServer.Thread_shell
import MaskServer.Thread_udp

class Server:
    def run(self):
        shellThread=MaskServer.Thread_shell.Thread_shell()
        shellThread.start()

        udpThread=MaskServer.Thread_udp.Thread_udp()
        udpThread.start()

if __name__=="__main__":
    maskServer=Server()
    maskServer.run()
