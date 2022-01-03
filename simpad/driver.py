"""
This script was created entirely by Ashe Muller over the course of literally an entire day.
Please, do credit me if you use this driver. I actually had to do this from the bottom up.
"""

from pywinusb import hid
import textwrap
import ctypes

class SimpadDriver:
    def __init__(self):
        self.device = self.get_device()
        if self.device:
            self.device.open()

    def get_device(self):
        filter = hid.HidDeviceFilter(vendor_id = 0x8088, product_id = 0x0006) #Simpad v2 Anniversary Edition
        devices = filter.get_devices()
        hid_device = filter.get_devices()
        if len(devices) > 0:
            return hid_device[0]
        else:
            print("No devices found")
            return False

    def getHexes(self, category):
        ## First is the key (06 for left, 07 for right) followed by the 3 split up hexes for the rgb, followed by 0x04 
        ## (100% brightness) and finished with 0xFB
        match category: # I was unable to automate the creation of hex, unfortuantely.
            case "300":
                return [0x07, 0x00, 0x00, 0xFF, 0x04, 0xFB] ## Blue
            case "100":
                return [0x07, 0x00, 0xFF, 0x00, 0x04, 0xFB] ## Green
            case "50":
                return [0x07, 0xFF, 0xEB, 0x00, 0x04, 0x10] ## Yellow
            case "miss":
                return [0x07, 0xFF, 0x00, 0x00, 0x04, 0xFB] ## Red
    
    def changeRGB(self, hitCategory):
        key = [0x06,0x07]
        for k in range(2):
            buffer= [0x00]*65
            bufferIn = self.getHexes(hitCategory)
            for y in range(6):
                buffer[y]=bufferIn[y-1]
            ## Change oaround a few values that fail to get edited usually
            buffer[0]=0x00
            buffer[1]=key[k-1]
            buffer[6]=bufferIn[5]
            out_report = self.device.find_output_reports()
            out_report[0].set_raw_data(buffer)
            out_report[0].send()

    def turnOff(self):
        """
        Turns off the pad
        """
        
        buffer= [0x00]*65
        bufferIn = [0x08, 0x03, 0xFF, 0xFF, 0x04, 0x07]
        for y in range(6):
            buffer[y]=bufferIn[y-1]
        ## Change oaround a few values that fail to get edited usually
        buffer[0]=0x00
        buffer[6]=bufferIn[5]
        out_report = self.device.find_output_reports()
        out_report[0].set_raw_data(buffer)
        out_report[0].send()

    def turnOn(self):
        """
        Turns on the pad
        """
        
        buffer= [0x00]*65
        bufferIn = [0x08, 0x02, 0xFF, 0xFF, 0x04, 0x06]
        for y in range(6):
            buffer[y]=bufferIn[y-1]
        ## Change oaround a few values that fail to get edited usually
        buffer[0]=0x00
        buffer[6]=bufferIn[5]
        out_report = self.device.find_output_reports()
        out_report[0].set_raw_data(buffer)
        out_report[0].send()
    
    def blackout(self):
        """
        Resets color to black
        """
        key = [0x06,0x07]
        for k in range(2):
            buffer= [0x00]*65
            bufferIn = [0x06, 0x00, 0x00, 0x00, 0x04, 0x04]
            for y in range(6):
                buffer[y]=bufferIn[y-1]
            ## Change oaround a few values that fail to get edited usually
            buffer[0]=0x00
            buffer[1]=key[k-1]
            buffer[6]=bufferIn[5]
            out_report = self.device.find_output_reports()
            out_report[0].set_raw_data(buffer)
            out_report[0].send()

pad = SimpadDriver()
