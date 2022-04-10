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

baudrate = 9600
serialport = "/dev/ttyUSB2"
usb = serial.Serial(serialport, baudrate, timeout=0.5)
usb.setDTR(False)
usb.setRTS(False)

#civ = ["0xfe","0xfe","0xA4","0xe0","0x00","0x56","0x34","0x12","0x07","0x00","0xfd"]
civ = ["0xFE", "0xFE", "0xA4", "0xE0", "0x15", "0x15", "0xFD"]

for value in civ:
    print(value)
    data = int(bytes(value).encode("utf-8"), 16)
    usb.write(struct.pack('>B', data))

byteData = usb.read(size=10) #Set size to something high
usb.close()

# End properly

exit()