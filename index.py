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

civ = "fe,fe,A4,e0,00,56,34,12,07,00,fd,"

civ = civ[:-1]
civ = civ.split(',')

'''
for value in civ:
    print(value)
    data = int(bytes(value).encode("utf-8"), 16)
    usb.write(struct.pack('>B', data))
'''

for value in civ:
    value = '0x' + value
    data = int(bytes(value).encode("utf-8"), 16)
    usb.write(struct.pack('>B', data))


response = ""
data = usb.read(size=16) #Set size to something high
for value in data:
    response += value.encode("hex")

print(response)

usb.close()

# End properly

exit()