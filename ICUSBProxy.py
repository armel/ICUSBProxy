#!/usr/bin/env python3
'''
Copyright (c) F4HWN Armel. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
Usage: ./ICUSBProxy.py [port] [error level]
'''

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import cgi
import serial

name = "ICUSBProxy"
version = "0.0.5"
client_timeout = 0.01
server_verbose = 0

ic_smeter = {
    "S":            "fe,fe,00,e0,15,02,fd",
    #"SWR":          "fe,fe,00,e0,15,12,fd",
    #"PWD":          "fe,fe,00,e0,15,11,fd",
    #"DataMode":     "fe,fe,00,e0,1a,06,fd",
    #"Frequency":    "fe,fe,00,e0,03,fd",
    #"Mode":         "fe,fe,00,e0,04,fd",
    #"TX":           "fe,fe,00,e0,1c,00,fd"
}

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_error(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if server_verbose > 1:        
            logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))

        # Init
        civ = str(self.path).split('=')

        response = ''
        request = civ[0]

        if(len(civ) == 2):
            civ = civ[1]

            civ = civ.split(',')

            if(len(civ) > 3):

                #civ = 'fe,fe,a4,e0,00,56,34,12,07,00,fd,115200,/dev/ttyUSB2'  # Debug trace
                #civ = 'fe,fe,a4,e0,03,fd,115200,/dev/ttyUSB2'                 # Debug trace

                client_serial = civ.pop()
                client_baudrate = civ.pop()
                client_address = civ[2]

                command = []

                try:
                    usb = serial.Serial(client_serial, client_baudrate, timeout=client_timeout)
                    
                    for value in civ:
                        command.append(int(value, 16))

                    usb.write(serial.to_bytes(command))

                    data = usb.read(size=16) # Set size to something high
                    for value in data:
                        response += '{:02x}'.format(value)

                    # Check if bad response    
                    if(response == "fefee0" + client_address + "fafd"):
                        response = ''

                    if server_verbose > 0:
                        print('Serial device ' + client_serial + ' is up...')

                    usb.close();
                except:
                    if server_verbose > 0:
                        print('Serial device ' + client_serial + ' is down...')
                    self._set_error()
            else:

                #civ = 'a4,115200,/dev/ttyUSB2'     # Debug trace
                #civ = 'a4,115200,/dev/ttyUSB2'     # Debug trace

                client_serial = civ.pop()
                client_baudrate = civ.pop()
                client_address = civ.pop()

                print(client_serial, client_baudrate, client_address)

                try:
                    usb = serial.Serial(client_serial, client_baudrate, timeout=client_timeout)

                    # Send command
                    for element in ic_smeter:
                        civ = ic_smeter[element]
                        civ = civ.replace("00", client_address)
                        civ = civ.split(',')


                        print(civ)
                        print(command)
                        for value in civ:
                            command.append(int(value, 16))

                        print(command)
                        print(civ)

                        usb.write(serial.to_bytes(command))

                        data = usb.read(size=16) # Set size to something high
                        for value in data:
                            response += '{:02x}'.format(value)

                        # Check if bad response    
                        if(response == "fefee0" + client_address + "fafd"):
                            response = ''

                        if server_verbose > 0:
                            print('Serial device ' + client_serial + ' is up...')

                    print("la")
                    usb.close();
                except:
                    if server_verbose > 0:
                        print('Serial device ' + client_serial + ' is down...')
                    self._set_error()

        else:
            if server_verbose > 0:
                print('Bad request ' + request)
                self._set_error()

        # End properly        
        try:
            self._set_response()
            self.wfile.write("{}".format(response).encode('utf-8'))
        except:
            self._set_error()

    def log_message(self, format, *args):
        return

def run(server_class=HTTPServer, handler_class=S, port=1234):
    if server_verbose > 1:
        logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting ' + name + ' v' + version + ' HTTPD on Port', port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping ' + name + ' v' + version + ' HTTPD...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        server_verbose = 0
        run(port=int(argv[1]))
    elif len(argv) == 3:
        server_verbose = int(argv[2])
        run(port=int(argv[1]))
    else:
        run()