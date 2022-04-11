#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
import settings as s
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import cgi
import serial

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        civ = str(self.path).split('=')
        civ = civ[1]

        usb = serial.Serial(s.client_serial, s.client_baudrate, timeout=0.1)
        usb.setDTR(False)
        usb.setRTS(False)

        #civ = 'fe,fe,a4,e0,00,56,34,12,07,00,fd,'  # Debug trace
        #civ = 'fe,fe,a4,e0,03,fd,'                 # Debug trace

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
        self.send_response(200)
        self.wfile.write("{}".format(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()