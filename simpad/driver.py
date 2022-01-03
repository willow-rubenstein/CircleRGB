from pywinusb import hid

filter = hid.HidDeviceFilter(vendor_id = 0x8088, product_id = 0x0006) #Simpad v2 Anniversary Edition
devices = filter.get_devices()
hid_device = filter.get_devices()
device = hid_device[0]
device.open()
buffer= [0x00]*65
bufferIn = [0x07, 0xFF, 0xFF, 0xFF, 0x04, 0xFB]
for i in range(6):
    buffer[i]=bufferIn[i-1]
buffer[0]=0x00
buffer[6]=0xFB
arr = (ctypes.c_byte * len(buffer))(*buffer)

out_report = device.find_output_reports()
out_report[0].set_raw_data(buffer)
out_report[0].send()