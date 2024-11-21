

from dataclasses import dataclass
import time
from threading import Event, Thread
from typing import Literal
from ur.eseries import RTDE, ConfigFile, URERobot



@dataclass
class RTDERegDef:
    name:Literal["input_double_register_0", 
                 "input_double_register_1",
                 "input_double_register_2",
                 "input_double_register_3",
                 "input_double_register_4",
                 "input_double_register_5",
                 "input_int_register_0",
                 "output_int_register_0"
                 ] 
    types:Literal["DOUBLE", 
                 "UINT32",
                 "INT32"
                 ]


@dataclass
class SimpleRTDEReg:
    WatchDog:RTDERegDef = RTDERegDef(name="input_int_register_0", types="INT32")
    Input0:RTDERegDef = RTDERegDef(name="input_double_register_0", types="DOUBLE")
    Output0:RTDERegDef = RTDERegDef(name="output_int_register_0", types="INT32")






class SimpleRTDE:
   
    FREQUENCY = 125

    def __init__(self, ip:str) -> None:
        
        self.robot = URERobot(ip, autoConnect=True)

        self.rtde = self.robot.createRTDEInterface()

        self._initRTDEParams()

        self.recvLoopThread = Thread(target=self.rtdeThread, daemon=True, name="RtdeRecvLoopThread")
        self.recvLoopThread.start()



    def _initRTDEParams(self):
        self.rtde.send_output_setup([SimpleRTDEReg.Output0.name],[SimpleRTDEReg.Output0.types])
        self.input0 = self.rtde.send_input_setup(variables=[SimpleRTDEReg.Input0.name], types=[SimpleRTDEReg.Input0.types])  # Configure an input package that the external application will send to the robot controller
        self.watchdog = self.rtde.send_input_setup(variables=[SimpleRTDEReg.WatchDog.name], types=[SimpleRTDEReg.WatchDog.types])
        self.rtde.send_start()


    def rtdeThread(self):
        while True:
            self.rtdeRecvState = self.rtde.receive()
            # self.rtde.send(self.watchdog)
            # self.rtde.send(self.setp)


    def sendInput0(self, data):
        self.input0.__dict__[SimpleRTDEReg.Input0.name] = round(data, 6)
        self.rtde.send(self.input0)

    
    def sendWatchDog(self, state:int):
        self.watchdog.__dict__[SimpleRTDEReg.WatchDog.name] = int(state)
        self.rtde.send(self.watchdog)





if __name__ == "__main__":
    
    import math
    simpleRtde = SimpleRTDE("192.168.1.103")

    watchDog = 0
    intput = 0.001
    simpleRtde.sendWatchDog(watchDog)

    time.sleep(1)

    while 1:
        simpleRtde.sendWatchDog(watchDog)
        simpleRtde.sendInput0(intput)

        time.sleep(0.002)
        watchDog += 1
        intput += 0.001
        print(simpleRtde.rtdeRecvState.__dict__)