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

    def get_device(self):
        filter = hid.HidDeviceFilter(vendor_id = 0x8088, product_id = 0x0006) #Simpad v2 Anniversary Edition
        devices = filter.get_devices()
        hid_device = filter.get_devices()
        if len(devices) > 0:
            return hid_device[0]
        else:
            print("No devices found")
            return False
    
    def changeRGB(self, hexes):
        vals = textwrap.wrap(hexes, 2)
        colorHexes = [] # Create a temp list of our color hex as a list of hexes with 4 characters each (i.e. 0xFF)
        for val in vals:
            colorHexes.append(hex(int("0x"+val, 16)))
        for i in range(2):
            x = i+5
            buffer= [0x00]*65
            ## First is the key (06 for left, 07 for right) followed by the 3 split up hexes for the rgb, followed by 0x04 
            ## (100% brightness) and finished with 0xFB
            bufferIn = [hex(int("0x0"+str(x), 16)), colorHexes[0], colorHexes[1], colorHexes[2], 0x04, 0xFB] 
            for i in range(6):
                buffer[i]=bufferIn[i-1]
            buffer[6]=0xFB
            arr = (ctypes.c_byte * len(buffer))(*buffer)
            self.device.send_output_report(arr)

