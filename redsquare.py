# Redsquare
VERSION = "0.10"
# Copyright (c) 2017 full phat products
#
# Usage: python reqsquare.py [port]
#
# [port] will default to 6789 if not supplied
#
# Credit to binary tides for python threaded socket code
#
# 0.10 - Fixed unicode character printing issues
#
# 0.9 - No longer returns response as HTML
#
# 0.8 - V2 API now returns JSON result
#
# 0.7 - bumped
#
# 0.6 - renamed some internal functions
#
# 0.5 - modded unicornhat.device to share new Unicorn lib
#
#     - ignores 'facicon.ico' browser requests
#
# 0.4 - added very basic support for the Pimoroni Unicorn Hat HD
#
# 0.3 - added support for the PCD8544 LCD display used in the
#	orignal Nokia 3310 phones
#
#     - Introduced V2 API which identifies the device required in the path
#
# 0.2 - added basic support for the Unicorn Hat using Pimoroni's own library
#
# 0.1 - renamed to RedSquare
#
#
#
import sys
import socket
import signal
import threading
import urllib
from urlparse import urlparse, parse_qs
import os
import importlib
import sos

import json


_currentDevice = ""
libs = { }
HOST = ""
PORT = 6789

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# helpers

def IsInt(str):
    try:
        int(str)
        return True
    except:
        return False

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# SIGINT handler
#
def signal_handler(signal, frame):
    print ''
    sos.sos_warn('SIGINT received: ending...')
    s.close()
    sys.exit()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# attempt to load the specified device handler and, if it
# loads okay, initialise it by calling its Init() method
#
def open_device(name):
    sos.sos_info("opening " + name + ".device...")

    global libs
    global _currentDevice

    sos.SetDevice(name)

    try:
        lib = importlib.import_module("rs_" + name, package=None)
        success = getattr(lib, 'init')()
        sos.ClrDevice()

        if success:
	    sos.sos_ok(name + ".device loaded ok")
            libs[name] = lib

        else:
	    sos.sos_fail(name + ".device failed to initialise")

    except:
        sos.ClrDevice()
	sos.sos_fail(name + ".device not found")


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# load up device handlers - should be more dynamic (e.g.
# from a .conf file, or enumerating a directory)
#
def get_devices():
    print ""
    sos.sos_info("Loading device handlers...")
    open_device("null")
    open_device("max7219")
    open_device("blink1")
    open_device("unicornhat")
    open_device("pcd8544")
    open_device("unicornhathd")
#    open_device("xxx")			# test failure

    sos.sos_note("Loaded device handlers")

#    print libs

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# helper: retrieve the requested URL from a standard HTTP request
#
def get_url(request):
    uri = ''
    lines = request.split('\r\n', 1)
    if len(lines) > 0:
        header = lines[0]
        chunks = header.split(' ')
        if len(chunks) == 3:
            uri = chunks[1]

    #return urllib.unquote(uri.lstrip('/'))
    return uri.lstrip('/')




#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# query handler
# return bool,string Tuple (e.g True,"OK") if query was
# handled, or false otherwise
#
def handle(queryDict):
    global libs
    _device = ""

    if 'device' in queryDict:
        _device = queryDict['device'][0]

    try:
        dev = libs[_device]
        if dev == None:
            print "[FAIL]: bad: " + _device
            return False, "bad device '" + _device + "'"

    except:
        print "[FAIL]: unknown device: " + _device
        return False, "Unknown device '" + _device + "'"

    # return the result of calling handler->handle()
    return getattr(dev, 'handle')(queryDict)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# v2 query handler
# return bool,string Tuple (e.g True,"OK") if query was
# handled, or false otherwise
#
def handle_v2(device, unit, queryDict):
    global libs

    result = False
    hint = "Unknown device '" + device + "'"

    sos.sos_info("Using V2 API")
    sos.sos_info("Looking for device '" + device + "'...")

    try:
        dev = libs[device]
        if dev != None:
            sos.SetDevice(device)

            # return the result of calling handler->handle()
            result,hint = getattr(dev, 'handle')(queryDict, 2, unit)

        else:
            sos.sos_fail(hint)

    except TypeError:
        hint = "This device does not support the V2 API"
        sos.sos_fail(hint)

    except Exception, e:
        hint = "Error communicating with device: " + str(e)
        sos.sos_fail(hint)

    sos.ClrDevice()

    # translate the result into JSON...

    myResult = { 'success': False, 'status': 200, 'hint': "" }

    # on failure, hint can be used to explain what went wrong
    # on success, hint can be used to include supplementary information

    myResult['success'] = result
    myResult['hint'] = hint

    # status is either 200 (success) or 400 (failure) for now...
    if not result:
        myResult['status'] = 400

    # still return true/false back up...
    return result, json.dumps(myResult, indent=2)

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# NOT USED
#
def do_io_thread(deviceObj, queryDict, apiVersion, unit):

    # return the result of calling handler->handle()
    result,hint = getattr(deviceObject, 'handle')(queryDict, apiVersion, unit)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# connection handler
# 
def client_thread(conn):

    global sos

    request = conn.recv(4096)
    uri = get_url(request)
    sos.sos_note("Request is '" + uri + "'")

    success = False
    response = 'BadRequest'

    try:
        o = urlparse(uri.strip('/'))
        #print 'query: ' + o.query
        #print 'path: ' + o.path

    except:
        sos.sos_fail("Couldn't parse the URL")

    # if empty path return welcome text...

    if o.path == "":
        sos.sos_warn("Empty path: returning our version info")
        response = 'Welcome to RedSquare ' + VERSION + '!<br>Copyright (c) 2017 full phat products<br>See http://fullphat.net/redsquare/ for more details<br>'

    elif o.path == "favicon.ico":
        sos.sos_info("Ignoring favicon request...")

    else:
        # split the path up...
        path = o.path.split('/')

        # check api version...
        if path[0] == 'v1':
            # return result of v1 handler...
            d = parse_qs(o.query)
            success,response = handle(d)

        elif path[0] == 'v2':
            # v2 api expects following syntax: /v2/{device}[/{unit=0}]?args...
            unit = 0
            if len(path) > 1:
                # get unit
                if len(path) > 2:
                    s = path[2]
                    if IsInt(s):
                        unit = int(s)
                    else:
                        sos.sos_warn("(V2) '" + s + "' is not a valid unit number")

                # return result of v2 handler...
                d = parse_qs(o.query)
                success,response = handle_v2(path[1], unit, d)

            else:
                sos.sos_warn("(V2) Missing device from path")

        else:
            sos.sos_fail("Invalid api version specified")

    # build the http reply...
    #body = "<html><body>" + response + "</body></html>"

    body = response
    reply = 'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(body)) + '\r\n\r\n' + body + '\r\n\r\n'

    # send it and close the socket...
    if success:
        sos.sos_ok('Sending success reply "' + response + '"...')

    else:
        sos.sos_warn('Sending failure reply "' + response + '"...')

    conn.sendall(reply)
    conn.close()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# main()
#

print ''
sos.sos_note('RedSquare ' + VERSION)
print 'Copyright (c) 2016-2017 full phat products'

if len(sys.argv) > 1:
    if sys.argv[1] == '-?' or sys.argv[1] == '--help':
        print 'Usage: python RedSquare.py [port]'
        sys.exit()

    try:
        PORT = int(sys.argv[1])

    except:
        sos.sos_fail('Invalid port specified: ' + sys.argv[1])
        sys.exit()

# install SIGINT signal handler
signal.signal(signal.SIGINT, signal_handler)

# load up our device handlers...
get_devices()

# start listening...
sos.sos_info("Opening socket...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))

except socket.error as msg:
    #print '  [Error] Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sos.sos_fail('Bind failed: you most likely already have something listening on port ' + str(PORT))
    sys.exit()
     
s.listen(10)

print ""
sos.sos_note('RedSquare ' + VERSION)
sos.sos_note('Now listening for incoming requests on port ' + str(PORT))
print ""
 
# loop until we get a SIGINT...

while 1:
    # accept a connection
    conn, addr = s.accept()
    sos.sos_info('Connection made from ' + addr[0] + ':' + str(addr[1]))
    thread = threading.Thread(target=client_thread, args=(conn,))
    thread.daemon = True
    thread.start()
