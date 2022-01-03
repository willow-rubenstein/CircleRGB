"""
This script was created entirely by Ashe Muller over the course of literally an entire day.
Please, do credit me if you use this driver. I actually had to do this from the bottom up.
"""

from pywinusb import hid

class SimpadDriver:
    def __init__(self):
        self.device = self.get_device()
        if self.device:
            self.device.open()

    def get_device(self):
        """ 
        Returns the first device found with the vendor id for simPad (0x8088)
        """
        filter = hid.HidDeviceFilter(vendor_id = 0x8088) # Filter by the SimPad vendor ID
        devices = filter.get_devices()
        print(devices)
        if len(devices) > 0: # Make sure there is at least 1 device with the vendor ID
            print("device found!")
            return devices[0]
        else:
            print("No devices found")
            return False

    def getHexes(self, rgb):
        """
        First is the key (06 for left, 07 for right) followed by the r,g,b values, followed by 0x04 
        (100% brightness), and finished with elements 2-5 to each other's powers consecutively as hex
        """
        arr = [0x07, rgb[0], rgb[1], rgb[2], 0x04, 0x00]
        arr[5] = arr[1] ^ arr[2] ^ arr[3] ^ arr[4]
        hexes = [hex(x) for x in arr]
        return hexes  
    
    def changeRGB(self, rgb):
        key = [0x06,0x07]
        for k in range(2):
            buffer= [0x00]*65
            bufferIn = self.getHexes(rgb) ## New in this version: I figured out how to get the rgb lmao
            for y in range(6):
                buffer[y]=bufferIn[y-1]
            ## Change around a few values that fail to get edited usually
            buffer[0]=0x00
            buffer[1]=key[k-1]
            buffer[6]=bufferIn[5]
            out_report = self.device.find_output_reports()
            out_report[0].set_raw_data(buffer)
            out_report[0].send()
    
    def blackout(self):
        """
        Resets color to black (Used when transitioning in between levels and the menu, restarting songs (still not fixed yets), etc.)
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