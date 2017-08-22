# Redsquare
VERSION = "0.6"
# Copyright (c) 2017 full phat products
#
# Usage: python reqsquare.py [port]
#
# [port] will default to 6789 if not supplied
#
# Credit to binary tides for python threaded socket code
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
from urlparse import urlparse, parse_qs
import os
import importlib
import sos
_currentDevice = ""
libs = { }
HOST = ""
PORT = 6789

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Terminal colours
#
class bcolors:
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def sos_warn(text):
    global _currentDevice
    s = bcolors.WARNING
    if _currentDevice != "":
        s = s + "       {" + _currentDevice + "} "
    print s + "[WARN] " + text + bcolors.ENDC

def sos_fail(text):
    global _currentDevice
    s = bcolors.FAIL
    if _currentDevice != "":
        s = s + "       {" + _currentDevice + "} "
    print s + "[FAIL] " + text + bcolors.ENDC

def sos_ok(text):
    global _currentDevice
    s = bcolors.OKGREEN
    if _currentDevice != "":
        s = s + "       {" + _currentDevice + "} "
    print s + "[ OK ] " + text + bcolors.ENDC

def sos_out(text):
    global _currentDevice
    s = bcolors.OKBLUE
    if _currentDevice != "":
        s = s + "       {" + _currentDevice + "} "
    print s + "[INFO] " + text + bcolors.ENDC

def sos_print(text):
    global _currentDevice
    s = ""
    if _currentDevice != "":
        s = s + "       {" + _currentDevice + "} "
    print s + "[INFO] " + text

def sos_info(text):
    global _currentDevice
    s = bcolors.WHITE
    if _currentDevice != "":
        s = s + "       {" + _currentDevice + "} "
    print s + text + bcolors.ENDC

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
    sos_warn('SIGINT received: ending...')
    s.close()
    sys.exit()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# attempt to load the specified device handler and, if it
# loads okay, initialise it by calling its Init() method
#
def open_device(name):
    sos_out("opening " + name + ".device...")

    global libs
    global _currentDevice

    sos.SetDevice(name)

    try:
        lib = importlib.import_module("rs_" + name, package=None)
        success = getattr(lib, 'init')()
        sos.ClrDevice()

        if success:
	    sos_ok(name + ".device loaded ok")
            libs[name] = lib

        else:
	    sos_fail(name + ".device failed to initialise")

    except:
        sos.ClrDevice()
	sos_fail(name + ".device not found" + bcolors.ENDC)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# load up device handlers - should be more dynamic (e.g.
# from a .conf file, or enumerating a directory)
#
def get_devices():
    print ""
    sos_info("Loading device handlers...")
    open_device("null")
    open_device("max7219")
    open_device("blink1")
    open_device("unicornhat")
    open_device("pcd8544")
    open_device("unicornhathd")
#    open_device("xxx")			# test failure

    sos_info("Loaded device handlers")

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

    sos.SetDevice(device)

    sos_out("(V2) Looking for device '" + device + "'...")
    try:
        dev = libs[device]
        if dev != None:
            # return the result of calling handler->handle()
            result,hint = getattr(dev, 'handle')(queryDict, 2, unit)

            # talk to the device using a new thread...
            #thread = threading.Thread(target=do_io_thread, args=(dev,queryDict,2,unit))
            #thread.daemon = True
            #thread.start()

        else:
            sos_fail("(V2) " + hint)

    except TypeError:
        hint = "This device does not support the V2 API"
        sos_fail("(V2) " + hint)

    except Exception, e:
        hint = "Error communicating with device: " + str(e)
        sos_fail("(V2) " + hint)

    sos.ClrDevice()
    return result,hint


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
    request = conn.recv(2048)

    uri = get_url(request)
    sos_print("Request is '" + uri + "'")

    success = False
    response = 'ERROR'

    try:
        o = urlparse(uri.strip('/'))
        #print 'query: ' + o.query
        #print 'path: ' + o.path

    except:
        sos_warn("couldn't parse the URL")
        response = 'Invalid URL supplied'

    # if empty path return welcome text...

    if o.path == "":
        sos_warn("null path: returning our version info")
        response = 'Welcome to RedSquare ' + VERSION + '!<br>Copyright (c) 2017 full phat products<br>See http://fullphat.net/redsquare/ for more details<br>'

    elif o.path == "favicon.ico":
        sos_out("ignoring favicon request")
        response = ""

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
                        sos_warn("(V2) '" + s + "' is not a valid unit number")

                # return result of v2 handler...
                d = parse_qs(o.query)
                success,response = handle_v2(path[1], unit, d)

            else:
                sos_warn("v2 api: missing device from path")
                response = "Missing {device} from path"

        else:
            sos_fail("invalid api version specified")
            response = "Invalid API version specified"

    # build the http reply...
    body = "<html><body>" + response + "</body></html>"
    reply = 'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(body)) + '\r\n\r\n' + body + '\r\n\r\n'

    # send it and close the socket...
    if success:
        sos_ok('Sending success reply "' + response + '"...')

    else:
        sos_fail('Sending failure reply "' + response + '"...')

    conn.sendall(reply)
    conn.close()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# main()
#
print ''
sos_info('RedSquare ' + VERSION)
print 'Copyright (c) 2016-2017 full phat products'

if len(sys.argv) > 1:
    if sys.argv[1] == '-?' or sys.argv[1] == '--help':
        print 'Usage: python RedSquare.py [port]'
        sys.exit()

    try:
        PORT = int(sys.argv[1])

    except:
        sos_fail('Invalid port specified: ' + sys.argv[1])
        sys.exit()

# install SIGINT signal handler
signal.signal(signal.SIGINT, signal_handler)

# load up our device handlers...
get_devices()

# start listening...
sos_info("Opening socket...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))

except socket.error as msg:
    #print '  [Error] Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sos_fail('Bind failed: you most likely already have something listening on port ' + str(PORT))
    sys.exit()
     
s.listen(10)

print ""
sos_info('RedSquare ' + VERSION)
sos_info('Now listening for incoming requests on port ' + str(PORT))
print ""
 
# loop until we get a SIGINT...

while 1:
    # accept a connection
    conn, addr = s.accept()
    sos_out('Connection made from ' + addr[0] + ':' + str(addr[1]))
    thread = threading.Thread(target=client_thread, args=(conn,))
    thread.daemon = True
    thread.start()
