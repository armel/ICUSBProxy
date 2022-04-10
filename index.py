#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi 
import time
import serial
import struct
from time import sleep

form = cgi.FieldStorage()
print("Content-type: text/html; charset=utf-8\n")

try:
    arg = cgi.FieldStorage()
    civ = arg['civ'].value
except:
    pass

baudrate = 115200
serialport = "/dev/ttyUSB2"
usb = serial.Serial(serialport, baudrate, timeout=0.5)
usb.setDTR(False)
usb.setRTS(False)

#civ = ["0xfe","0xfe","0xA4","0xe0","0x00","0x56","0x34","0x12","0x07","0x00","0xfd"]
#civ = ["0xfe", "0xfe", "0xa4", "0xe0", "0x15", "0x15", "0xfd"]     # Vd
#civ = ["0xfe", "0xfe", "0xa4", "0xe0", "0x15", "0x02", "0xfd"]     # Smeter
#civ = ["0xfe", "0xfe", "0xa4", "0xe0", "0x04", "0xfd"]             # Mode
civ = "fe,fe,a4,e0,15,02,fd,"

civ = civ.split(',')
for value in civ:
    print(value)
    #data = int(bytes(value).encode("utf-8"), 16)
    usb.write(value)

print('-----')
byteData = usb.read(size=16) #Set size to something high
print(len(byteData))
for value in byteData:
    print(value.encode("hex")),

usb.close()

# End properly

exit()