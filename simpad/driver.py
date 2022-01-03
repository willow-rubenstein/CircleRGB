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
        filter = hid.HidDeviceFilter(vendor_id = 0x8088) # Filter by the SimPad vendor ID
        devices = filter.get_devices()
        if len(devices) > 0: # Make sure there is at least 1 device with the vendor ID
            for item in devices:
                ## Search for product ID in list of all IDs
                if item.product_id in [0x0302, 0x0102, 0x0007, 0x0006, 0x0004, 0x0003, 0x0002, 0x0001]:
                    print(f"Found Simpad with Device ID {item.product_id}")
                    return item
        else:
            print("No devices found")
            return False

    def getHexes(self, rgb):
        ## First is the key (06 for left, 07 for right) followed by the 3 split up hexes for the rgb, followed by 0x04 
        ## (100% brightness) and finished with 0xFB
        return [0x07, hex(rgb[0]), hex(rgb[1]), hex(rgb[2]), 0x04, 0xFB]
        """
         match category: # I was unable to automate the creation of hex, unfortuantely.
                case "300":
                    return [0x07, 0x00, 0x00, 0xFF, 0x04, 0xFB] ## Blue
                case "100":
                    return [0x07, 0x00, 0xFF, 0x00, 0x04, 0xFB] ## Green
                case "50":
                    return [0x07, 0xFF, 0xEB, 0x00, 0x04, 0x10] ## Yellow
                case "miss":
                    return [0x07, 0xFF, 0x00, 0x00, 0x04, 0xFB] ## Red

        This block is commented out until I figure out what to do with it.
        I have to figure out the point of the 6th element in the list.
        """     
    
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
