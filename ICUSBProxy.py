#!/usr/bin/env python3

#
#  ICUSBProxyWS.py by @tobozo copyleft (c+) 2022
#
#  Scope: behaves like @armel's ICUSBProxy.py while providing some added features:
#
#    - Threading model
#      - Main thread = web server (legacy)
#      - PortsEnumerator = scans for changes on tty/COM connected devices
#      - Poll = runs subscriptions and publishes if needed
#    - Extended support for shared UART
#      - Ports enumeration
#      - Port sharing
#      - Persistence
#      - Concurrent access
#    - Inverted subscribe/publish data flow model
#      - M5 device subscribes via POST (devive, command, poll_delay, publish address)
#      - Proxy thread publishes to M5 device WebSocket when new data needs to be sent
#    - Demo/test mode based for IC705
#


import websocket
import random
import time
from datetime import datetime
import json
import serial
import serial.tools.list_ports
import threading
import logging
from threading import Thread, Lock
from http.server import BaseHTTPRequestHandler, HTTPServer

name           = "ICUSBProxy"
version        = "0.1.0"
client_timeout = 0.01
server_verbose = 2
demo_mode      = 0 # use this when no IC is actually connected, will send dummy data

UARTS      = [] # UART's are shared between HTTP Server and WebSockets/Serial thread, but also across M5 Devices
uart_count = 0
subscriptions_count = 0
M5Clients  = [] # M5Stack devices with registered subscriptions
connected_serial_ports = [] # currently connected COM/tty ports, repopulated every second
remote_serial_ports    = [] #
last_message = "" # to avoid repeated messages in the console
last_error = ""

def ConsolePrintError( e ):
    global last_error
    if server_verbose < 2 and last_error == e:
        # ignore repeated errors unless verbosity is high
        return
    now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print( [now, "[ERROR]", e] )
    last_error = e

last_message = ''
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

class UART():
    def __init__(self):
        self.id     = None # unique id (incremented)
        self.tty    = None # tty name e.g. /dev/ttyUSBxx
        self.bauds  = None # baud rate e.g. 115200
        self.serial = None # serial instance, e.g. self.serial = serial.Serial(tty, bauds, timeout=client_timeout)
        self.mutex  = None # mutex for shared access, e.g. self.mutex = threading.Lock()

class M5Socket():
    def __init__(self):
        self.id            = None
        self.host          = None # Hostname/IP of the WS server on the M5Stack
        self.subscriptions = None # Array of subscriptions
        self.ws            = None # WebSocket instance, e.g. self.ws = websocket.WebSocket()

# Subscriptions are stored in in M5Socket().subscriptions as an array
class Subscription():
    def __init__(self):
        self.id            = None # Unique ID for subscription
        self.cmd           = None # CIV command, e.g. 'fefea4e01502fd'
        self.uart          = None # UART() shared object
        self.freq          = None # Polling frequency
        self.last_poll     = None # Last polling time
        self.last_response = None # Cache for last response

def initSerial( tty, bauds ):
    try:
        if tty.find("://") != -1:
            #print("Remote UART: " + tty );
            uart = serial.serial_for_url( tty, bauds )
        else:
            #print("Local UART: " + tty );
            uart = serial.Serial( tty, bauds, timeout=client_timeout )
        return uart
    except Exception as e:
        ConsolePrintMessage(tty + " not reachable")
        return None

def GetCIVResponse( request, response_data ):
    response = ''
    for value in response_data:
        response += '{:02x}'.format(value)
    # test: 2 first bytes must match, bytes 3 and 4 are swapped
    if response[0:4]!=request[0:4] or response[4:6]!=request[6:8] or response[6:8]!=request[4:6]:
        try:
            decoded_response = bytes.fromhex(response)
        except Exception as e:
            decoded_response = response
        ConsolePrintError( ['invalid response:', decoded_response] )
    elif len(response_data) > 0 and response_data[-1] == 0xfd: # packet terminator
        return response
    else:
        ConsolePrintError( 'unterminated packet')
    return ''

def WSEmit( M5ClientId, message ):
    global M5Clients
    client = M5Clients[M5ClientId]
    try:
        client.ws.send( message )
        resp = client.ws.recv()
    except Exception as e:
        try:
            M5Clients[M5ClientId].ws.connect("ws://"+M5Clients[M5ClientId].host+"/ws", origin="icusbproxy.local")
            ConsolePrintMessage("A WebSocket connection was re-established for id #" + str( M5ClientId ) )
        except Exception as e:
            ConsolePrintMessage("WS for id #" + str( M5ClientId ) +" Connection lost")

def Poll( M5ClientId, SubscriptionId ):
    global M5Clients
    subscription = M5Clients[M5ClientId].subscriptions[SubscriptionId]
    if subscription.uart.serial == None:
        try:
            M5Clients[M5ClientId].subscriptions[SubscriptionId].uart.serial = initSerial(  subscription.uart.tty, subscription.uart.bauds )
            if subscription.uart.serial !=None:
                ConsolePrintMessage("Opening UART " + subscription.uart.tty + " succeeded" )
            else:
                return False
            #return True
        except Exception as e:
            ConsolePrintMessage("Opening UART " + subscription.uart.tty + " failed")
            return False

    # previous attempt to connect to serial failed, no need to go further
    if subscription.uart.serial == None:
        return False

    try:
        try:
            packet = bytearray.fromhex(subscription.cmd)
        except:
            ConsolePrintMessage("Invalid subscription packet: " + subscription.cmd)
            return False
        #subscription.uart.serial.read_all() # flush serial
        subscription.uart.serial.write( packet )
        time.sleep(0.1)
        data = subscription.uart.serial.read_until(b'\xfd')
        #data = subscription.uart.serial.read(size=16) # Set size to something high
        response = GetCIVResponse( subscription.cmd, data )
        if response == '' or response == None:
            ConsolePrintMessage(['Invalid data: ', data])
            return False
        else:
            if subscription.last_response != response:
                M5Clients[M5ClientId].subscriptions[SubscriptionId].last_response = response
                ConsolePrintMessage(["cmd=", subscription.cmd, "resp=", data.hex() ])
                WSEmit( M5ClientId, response )
            return True
    except Exception as e:
        M5Clients[M5ClientId].subscriptions[SubscriptionId].uart.serial = None
        ConsolePrintMessage("UART disconnected", e)
        WSEmit( M5ClientId, "UART DOWN" )
        return False

def HasPort( device ):
    global connected_serial_ports
    for port in connected_serial_ports:
        if device == port[0]:
            return True
    for port in remote_serial_ports:
        if device == port[0]:
            return True

    return False

# Daemon
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

# Daemon
def UARTPoller():
    while True:
        global M5Clients, UARTS, connected_serial_ports, uart_message
        sleep_time = 1
        for M5ClientId, M5Client in enumerate(M5Clients):
            for SubscriptionId, subscription in enumerate( M5Client.subscriptions ):
                sleep_time = min( subscription.freq, sleep_time )
                now = time.time()
                if subscription.last_poll + subscription.freq < now:
                    M5Clients[M5ClientId].subscriptions[SubscriptionId].last_poll = now
                    if HasPort( subscription.uart.tty ) == True:
                        # get mutex to avoid collision with the main thread
                        M5Clients[M5ClientId].subscriptions[SubscriptionId].uart.mutex.acquire()
                        if Poll( M5ClientId, SubscriptionId ) != True:
                            ConsolePrintMessage("UART Polling failed")
                            #WSEmit( M5Client.id, "UART DOWN" )
                        M5Clients[M5ClientId].subscriptions[SubscriptionId].uart.mutex.release()

                        if subscription.freq == 0: # one time subscription self-deletes after use
                            M5Clients[M5ClientId].subscriptions.remove( subscription )
                    else:
                        if demo_mode == 1:
                            cmd = str(subscription.cmd)
                            resp = demo_response( cmd[4:6], cmd[6:8], cmd[8:14] )
                            if resp != False:
                                WSEmit( M5Client.id, resp )
                            else:
                                print("Bad command ",  cmd[6:8], cmd[8:14] )
                        else:
                            ConsolePrintError( subscription.uart.tty + " is not available" )
                            WSEmit( M5Client.id, "UART DOWN" )

        time.sleep( sleep_time ) # avoid loopbacks


class S(BaseHTTPRequestHandler):


    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_error(self):
        self.send_response(500)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


    def do_OPTIONS(self):
        # handle CORS requests
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")

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
    print('Starting ' + name + ' v' + version + ' WebSocket Client and HTTPD Server on Port', port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

    print("\n")
    # close all open UARTS
    for uart in UARTS:
        if uart.serial != None:
            print("Closing UART " + uart.tty )
            uart.serial.close()

    print('Stopping ' + name + ' v' + version + ' HTTPD...\n')



if __name__ == "__main__":

    # spawn a new thread to scan for serial devices with an active connection
    port_controller = threading.Thread(target=PortsEnumerator, name="PortsScan")
    port_controller.setDaemon(True)
    port_controller.start()

    # spawn a new thread and attach the UART Poller
    uart_poller = threading.Thread(target=UARTPoller, name='Daemon')
    uart_poller.setDaemon(True)
    uart_poller.start()

    # start the webserver on the main thread
    from sys import argv
    if len(argv) == 2:
        server_verbose = 0
        run(port=int(argv[1]))
    elif len(argv) == 3:
        server_verbose = int(argv[2])
        run(port=int(argv[1]))
    else:
        run()

