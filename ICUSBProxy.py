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
import threading
import serial
import serial.tools.list_ports

name = "ICUSBProxy"
version = "0.0.5"
client_timeout = 0.01
server_verbose = 0

connected_serial_ports = [] # currently connected COM/tty ports, repopulated every second
last_message = ""
UARTS      = [] # UART's are shared between HTTP Server and WebSockets/Serial thread, but also across M5 Devices

def ConsolePrintMessage( msg, error=None ):
    global last_message, server_verbose
    if error!=None:
        ConsolePrintError( error )
    if server_verbose != 0:
        if server_verbose < 2 and last_message == msg:
            return
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print( [now, msg] )
        last_message = msg

def PortsEnumerator():
    global UARTS, connected_serial_ports
    while True:
        tmp_ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        #tmp_ports.append( remote_serial_ports )
        if len(tmp_ports)>len(connected_serial_ports):
            new_device = list(set(tmp_ports) - set(connected_serial_ports))
            ConsolePrintMessage(["New Device(s): ", new_device] )
            for uart in UARTS:
                if uart.tty == new_device[0]:
                    uart.serial = initSerial(  uart.tty, uart.bauds )
        elif len(tmp_ports)<len(connected_serial_ports):
            old_device = list(set(connected_serial_ports) - set(tmp_ports))
            ConsolePrintMessage(["Device(s) removed: ", old_device] )
        connected_serial_ports = tmp_ports
        time.sleep(1)

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

            #civ = 'fe,fe,a4,e0,00,56,34,12,07,00,fd,115200,/dev/ttyUSB2'  # Debug trace
            #civ = 'fe,fe,a4,e0,03,fd,115200,/dev/ttyUSB2'                 # Debug trace

            civ = civ.split(',')

            client_serial = civ.pop()
            client_baudrate = civ.pop()
            client_adresse = civ[2]

            try:
                usb = serial.Serial(client_serial, client_baudrate, timeout=client_timeout)
                
                # Send command
                command = []

                for value in civ:
                    command.append(int(value, 16))

                usb.write(serial.to_bytes(command))

                data = usb.read(size=16) # Set size to something high
                for value in data:
                    response += '{:02x}'.format(value)

                # Check if bad response    
                if(response == "fefee0" + client_adresse + "fafd"):
                    response = ''

                if server_verbose > 0:
                    print('Serial device ' + client_serial + ' is up...')

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

    # spawn a new thread to scan for serial devices with an active connection
    port_controller = threading.Thread(target=PortsEnumerator, name="PortsScan")
    port_controller.setDaemon(True)
    port_controller.start()

    from sys import argv

    if len(argv) == 2:
        server_verbose = 0
        run(port=int(argv[1]))
    elif len(argv) == 3:
        server_verbose = int(argv[2])
        run(port=int(argv[1]))
    else:
        run()