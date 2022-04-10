#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Copyright (c) F4HWN Armel. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
'''

import settings as s
import http.server
 
handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", s.server_port), handler) as httpd:
    print("serving at port", s.server_port)
    httpd.serve_forever()