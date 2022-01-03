import websocket as websockets
import json
from threading import Thread
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
import os
import subprocess
import time
import atexit
from simpad.driver import SimpadDriver


class appClient:
    def __init__(self):
        ## Remove this line if you are distibuting the app on a non-windows platform
        sim = SimpadDriver()
        self.isSimpad = False
        self.device = None
        if sim.device:
            self.isSimpad = True
            self.device = sim
            Thread(target=os.system, args=("gosumemory.exe",)).start()
        else:
            self.bootup()
            self.client = None
            self.keyboard = None
            self.startOpenRGBClient() # Shit fucking crashes every time, man

        self.currentScoreType = "0"
        print("Keyboard initialized successfully")

        self.scoreMap = {
            "300": 0,
            "100": 0,
            "50": 0,
            "miss": 0
        }

        self.tempScore = {} # Temp Real Score

        ## Define our RGB values for each different hit type
        self.rgbOptions = self.getOptions()
        score300 = self.rgbOptions["300"]
        score100 = self.rgbOptions["100"]
        score50 = self.rgbOptions["50"]
        scoreMiss = self.rgbOptions["miss"]
        if self.isSimpad != True:
            self.rgbMap = {
                "300": RGBColor(score300[0], score300[1], score300[2]),
                "100": RGBColor(score100[0], score100[1], score100[2]),
                "50": RGBColor(score50[0], score50[1], score50[2]),
                "miss": RGBColor(scoreMiss[0], scoreMiss[1], scoreMiss[2])
            }
        else:
            self.rgbMap = {
                "300": (score300[0], score300[1], score300[2]),
                "100": (score100[0], score100[1], score100[2]),
                "50": (score50[0], score50[1], score50[2]),
                "miss": (scoreMiss[0], scoreMiss[1], scoreMiss[2])
            }
    
    def startOpenRGBClient(self):
        x = True
        while x:
            try:
                self.client = OpenRGBClient()
                self.client.clear() # Turns everything off
                self.keyboard = self.client.get_devices_by_type(DeviceType.KEYBOARD)[0]
                x = False
            except:
                pass
            time.sleep(0.5)
    
    def getOptions(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                return json.load(f)
        else:
            with open("config.json", "w") as f:
                x = {
                    "300": (0,0,255),
                    "100": (0,255,0),
                    "50": (255,255,0),
                    "miss": (255,0,0)
                }
                json.dump(x, f)
                return x
    
    def bootup(self):
        ## For Windows Dist Only. Ignore for all other platforms
        os.startfile("gosumemory.exe")
        os.startfile(os.path.join("openRGB", "OpenRGB.exe"))
        subprocess.Popen(["openRGB/openRGB.exe", '--startminimized', '--server'])

    def run(self):
        websocket = websockets.WebSocketApp("ws://localhost:24050/ws",
                                        on_message=self.on_message)
        websocket.run_forever()     
                
    
    def clearKeyboard(self):
        self.keyboard.set_color(RGBColor(0,0,0), True)
    
    def resetStats(self):
        self.scoreMap = {
            "300": 0,
            "100": 0,
            "50": 0,
            "miss": 0
        }
        self.currentScoreType = "0"
        if not self.isSimpad:
            self.clearKeyboard()
        else:
            self.device.blackout()

    def on_message(self, ws, message):
        try:
            msg = json.loads(message)
            hits = msg["gameplay"]["hits"]
            if self.tempScore == {} and msg["menu"]["state"] == 2:
                self.tempScore = hits
            elif msg["gameplay"]["hits"] != self.tempScore and msg["menu"]["state"] == 2:
                self.tempScore = hits
                Thread(target=self.logicThread).start()
            elif msg["menu"]["state"] == 7:
                self.clearKeyboard()
            elif msg["menu"]["state"] == 0:
                self.tempScore = hits
                self.resetStats()
            if self.tempScore != hits:
                self.tempScore = hits
                self.resetStats()
        except:
            pass

    def itemLogic(self, key, value):
        try:
            temp = ""
            match key:
                case "300":
                    temp = "300"
                case "geki":
                    temp = "300"
                case "100":
                    temp = "100"
                case "katu":
                    temp = "100"
                case "50":
                    temp = "50"
                case "0":
                    temp = "miss"
            if value > self.scoreMap[temp] and temp != self.currentScoreType:
                self.currentScoreType = temp
                self.scoreMap[temp] = value
                self.setLight(temp)
        except:
            pass

    def logicThread(self):
        for item in list(self.tempScore.keys()):
            Thread(target=self.itemLogic, args=(item,self.tempScore[item],)).start()
    
    def setLight(self, hitType):
        if self.isSimpad:
            rgb = self.rgbMap[hitType]
            print(f"Changing light for hit type {hitType} for SimPad")
            self.device.changeRGB(rgb)
        else:
            rgb = self.rgbMap[hitType]
            print(f"Changing light for hit type {hitType} with rgb {rgb}")
            self.keyboard.set_color(rgb, False)

a = appClient()
a.run()

def exit_handler():
    """
    Handle Closing OpenRGB/gosumemory on program closed
    This one is also PC-Only, remove it if you're on another platform, 
    or change it to that platform's equivelant if you'd like
    """
    print("Closing OpenRGB/gosumemory")
    os.system("taskkill /im gosumemory.exe")
    if not a.isSimpad:
        os.system("taskkill /im OpenRGB.exe")

atexit.register(exit_handler)

