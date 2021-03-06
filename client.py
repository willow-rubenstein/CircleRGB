"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import websocket as websockets
import json
from threading import Thread
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
import os
import subprocess
import time
import atexit
from simpadlib import simpad


class appClient:
    def __init__(self):
        ## Remove this line if you are distibuting the app on a non-windows platform
        sim = simpad.Controller()
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
            
        print("Keyboard initialized successfully")

        ## Set Score-Related Class Variables
        self.currentScoreType = "0"
        self.scoreMap = {
            "300": 0,
            "100": 0,
            "50": 0,
            "miss": 0
        }
        self.tempScore = {} # Temp Real Score

        ## Define our RGB values for each different hit type
        self.rgbOptions = self.getOptions()
        score300 = tuple(int(self.rgbOptions["300"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        score100 = tuple(int(self.rgbOptions["100"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        score50 = tuple(int(self.rgbOptions["50"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        scoreMiss = tuple(int(self.rgbOptions["miss"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        if self.isSimpad != True:
            self.rgbMap = {
                "300": RGBColor(score300[0], score300[1], score300[2]),
                "100": RGBColor(score100[0], score100[1], score100[2]),
                "50": RGBColor(score50[0], score50[1], score50[2]),
                "miss": RGBColor(scoreMiss[0], scoreMiss[1], scoreMiss[2])
            }
        else:
            self.rgbMap = {
                "300": self.rgbOptions["300"],
                "100": self.rgbOptions["100"],
                "50": self.rgbOptions["50"],
                "miss": self.rgbOptions["miss"]
            }
    
    def startOpenRGBClient(self):
        """
        Runs a loop until it grabs the keyboard device connected via OpenRGB.
        Should probably fix this to where it only calls this function if the user
        actually has a keyboard that works with OpenRGB currently connected.
        """
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
        """
        Gets the user's preferences from the config file for RGB colors, and
        creates a new file if one doesn't exist with the default settings.
        """
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                return json.load(f)
        else:
            with open("config.json", "w") as f:
                x = {
                    "300": "#0000ff",
                    "100": "#00ff00",
                    "50": "#ffff00",
                    "miss": "#ff0000"
                }
                json.dump(x, f)
                return x
    
    def bootup(self):
        ## For Windows Dist Only. Ignore for all other platforms
        Thread(target=os.system, args=("gosumemory.exe",)).start()
        Thread(target=os.system, args=("openRGB\openRGB.exe --startminimized --server",)).start()

    def run(self):
        websocket = websockets.WebSocketApp("ws://localhost:24050/ws",
                                        on_message=self.on_message)
        websocket.run_forever()     
                
    def resetStats(self):
        self.scoreMap = {
            "300": 0,
            "100": 0,
            "50": 0,
            "miss": 0
        }
        self.currentScoreType = "0"
        if not self.isSimpad:
            self.keyboard.set_color(RGBColor(0,0,0), True)
        else:
            self.device.reset()

    def on_message(self, ws, message):
        try:
            msg = json.loads(message)
            hits = msg["gameplay"]["hits"]
            if self.tempScore == {} and msg["menu"]["state"] == 2:
                self.tempScore = hits
            if msg['gameplay']['score'] == 0:
                self.resetStats()
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
        rgb = self.rgbMap[hitType]
        print(f"Changing light for hit type {hitType}")
        if self.isSimpad:
            self.device.set_color(rgb, simpad.Keys.both)
        else:
            self.keyboard.set_color(rgb, False)

a = appClient()
a.run()

def exit_handler():
    """
    Handle closing OpenRGB on close (used to close 
    gosumemory as well, but now that runs in a thread.)
    """
    if not a.isSimpad:
        print("Closing OpenRGB")
        os.system("taskkill /im OpenRGB.exe")

atexit.register(exit_handler)

