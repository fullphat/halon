# Redsquare
VERSION = "0.3"
# Copyright (c) 2017 full phat products
#
# Usage: python reqsquare.py [port]
#
# [port] will default to 6789 if not supplied
#
# Credit to binary tides for python threaded socket code
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

_currentDevice = ''

libs = { }
 
HOST = ''
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

def sos_dev(text):
    global _currentDevice
    print "       [" + _currentDevice + "]: " + text

def sos_warn(text):
    print bcolors.WARNING + "[WARN] " + text + bcolors.ENDC

def sos_fail(text):
    print bcolors.FAIL + "[FAIL] " + text + bcolors.ENDC

def sos_ok(text):
    print bcolors.OKGREEN + "[ OK ] " + text + bcolors.ENDC

def sos_out(text):
    print bcolors.OKBLUE + "[INFO] " + text + bcolors.ENDC

def sos_print(text):
    print "[INFO] " + text

def sos_info(text):
    print bcolors.WHITE + text + bcolors.ENDC


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# SIGINT handler
#
def signal_handler(signal, frame):
    print ''
    sos_warn('SIGINT received: ending...')
    s.close()
    sys.exit()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# attempt to load the specified handler and, if it loads
# okay, initialise it by calling its Init() method
#
def load_handler(name):
    sos_out("opening " + name + ".device...")

    global libs
    global _currentDevice

    _currentDevice = name

    try:
        lib = importlib.import_module("rs_" + name, package=None)
        success = getattr(lib, 'init')()
        if success:
	    sos_ok(name + ".device loaded ok")
            libs[name] = lib

        else:
	    sos_warn(name + ".device failed to initialise")

    except:
	print bcolors.WARNING + "[WARN]: " + name + ".device not found" + bcolors.ENDC

    _currentDevice = ''


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# load up handlers - should be more dynamic (e.g. from
# a .conf file, or enumerating a directory)
#
def get_handlers():
    print ""
    sos_info("Loading device handlers...")
    load_handler("null")
    load_handler("max7219")
    load_handler("blink1")
    load_handler("unicornhat")
    load_handler("pcd8544")
    load_handler("xxx")			# test failure

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
def handle_v2(device, queryDict):
    global libs

    sos_out("(V2) Looking for device '" + device + "'...")
    try:
        dev = libs[device]
        if dev == None:
            sos_fail("(V2) Unknown device '" + device + "'")
            return False, "unknown device '" + device + "'"

    except:
        sos_fail("(V2) Unknown device '" + device + "'")
        return False, "unknown device '" + device + "'"

    # return the result of calling handler->handle()
    return getattr(dev, 'handle')(queryDict)


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

    else:

        # split the path up...
        path = o.path.split('/')

        # check api version...
        if path[0] == 'v1':
            # return result of v1 handler...
            d = parse_qs(o.query)
            success,response = handle(d)

        elif path[0] == 'v2':
            # v2 api expects following syntax: /v2/{device}?args...
            if len(path) == 2:
                # return result of v2 handler...
                d = parse_qs(o.query)
                success,response = handle_v2(path[1], d)

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
    sos_print('Sending reply "' + response + '"...')
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
get_handlers()

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
