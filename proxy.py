#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Copyright (c) F4HWN Armel. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
'''

import settings as s
import cgi 
import time
import serial

'''
print('Content-type: text/html; charset=utf-8\n')

try:
    arg = cgi.FieldStorage()
    civ = arg['civ'].value
except:
    civ = ','
'''

usb = serial.Serial(s.client_serial, s.client_baudrate, timeout=0.1)
usb.setDTR(False)
usb.setRTS(False)

#civ = 'fe,fe,a4,e0,00,56,34,12,07,00,fd,'  # Debug trace
civ = 'fe,fe,a4,e0,03,fd,'                 # Debug trace

# Send command

civ = civ[:-1]
civ = civ.split(',')
command = []

for value in civ:
    command.append(int(value, 16))

usb.write(serial.to_bytes(command))

# Receive response

response = ''

data = usb.read(size=16) # Set size to something high
for value in data:
    response += '{:02x}'.format(value)

# End properly

print('Content-type: text/html; charset=utf-8\n')
print(response)

usb.close()
exit()