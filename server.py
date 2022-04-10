#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Copyright (c) F4HWN Armel. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
'''

import settings as s
import http.server
 
server_address = ('localhost', s.server_port)

server = http.server.HTTPServer
handler = http.server.CGIHTTPRequestHandler
handler.cgi_directories = ['/']

print('Serveur actif sur le port :', s.server_port)

httpd = server(server_address, handler)
httpd.serve_forever()