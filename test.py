#!/usr/bin/env python3
'''
Copyright (c) F4HWN Armel. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
Usage: ./icom_civ_proxy.py [<port>]
'''

import serial

civ = 'fe,fe,a4,e0,03,fd,/dev/ttyUSB2,115900'                 # Debug trace
civ = civ.split(',')

client_serial = civ.pop()
client_baudrate = civ.pop()

print(client_serial)
print(client_baudrate)

usb = serial.Serial(str(client_serial), int(client_baudrate), timeout=0.02)
#usb.setDTR(False)
#usb.setRTS(False)

# Send command
command = []

for value in civ:
    command.append(int(value, 16))

usb.write(serial.to_bytes(command))

# Receive response
response = ''

data = usb.read(size=16) # Set size to something high
for value in data:
    response += '{:02x}'.format(value)

print(response)