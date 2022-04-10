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

    baudrate = 9600
    serialport = "/dev/ttyUSB2"
    usb = serial.Serial(serialport, baudrate)
    #sleep(0.5)
    usb.setDTR(False)
    usb.setRTS(False)

    civ = ["0xfe","0xfe","0xA4","0xe0","0x00","0x56","0x34","0x12","0x07","0x00","0xfd"]

    for value in civ:
        usb.write(struct.pack('>B', int(bytes(value), 'UTF-8'), 16)))
    usb.close()

except:
    pass

# End properly

exit()