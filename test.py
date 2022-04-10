#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
RRFBlockIP version Web
Learn more about RRF on https://f5nlg.wordpress.com
73 & 88 de F4HWN Armel
'''

import cgi
import sys
import getopt
import os
import re

print('Content-Type: application/html\n\n')

try:
    arg = cgi.FieldStorage()
    get_command = arg['command'].value

except:
    pass

print(get_command)
# End properly

exit()