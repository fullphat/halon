# RedSquare
VERSION = "0.2c"
# Copyright (c) 2017 full phat products
#
# Usage: python reqsquare.py [port]
#
# [port] will default to 6789 if not supplied
#
# Credit to binary tides for python threaded socket code
#
# 0.2 - added basic support for the Unicorn Hat using Pimoroni's own library
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

libs = { }
 
HOST = ''
PORT = 6789

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# SIGINT handler
#
def signal_handler(signal, frame):
    print ''
    print 'SIGINT received: ending...'
    s.close()
    sys.exit()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# attempt to load the specified handler and, if it loads
# okay, initialise it by calling its Init() method
#
def load_handler(name):
    print "[info]: opening " + name + ".device..."
    global libs
    try:
        lib = importlib.import_module("rs_" + name, package=None)
        success = getattr(lib, 'init')()
        if success:
	    print "[info]: " + name + ".device loaded ok"
            libs[name] = lib

        else:
	    print "[WARN]: " + name + ".device failed to initialise"

    except:
	print "[FAIL]: " + name + ".device not found"


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# load up handlers - should be more dynamic (e.g. from
# a .conf file, or enumerating a directory)
#
def get_handlers():
    print ""
    print "Loading device handlers..."
    load_handler("null")
    load_handler("max7219")
    load_handler("blink1")
    load_handler("unicornhat")
    load_handler("xxx")			# test failure
    print "Loaded device handlers"

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
# connection handler
# 
def client_thread(conn):
    request = conn.recv(2048)

    uri = get_url(request)
    print '[Info] Request is: ' + uri

    success = False
    response = 'ERROR'

    try:
        o = urlparse(uri.strip('/'))
        #print 'query: ' + o.query
        #print 'path: ' + o.path

    except:
        print "[Error] Couldn't parse the URL"
        response = 'Invalid URL supplied'

    if o.path != '':
        # check api version (path)
        if o.path == 'v1':
            d = parse_qs(o.query)
            success,response = handle(d)

        else:
            print "[Error] invalid api version specified"
            response = 'Invalid API version specified'

    else:
        # null URL supplied - do we want to return hint/welcome message?
        print "[Warn] null path: returning our version info"
        response = 'Welcome to RedSquare ' + VERSION + '!<br>Copyright (c) 2017 full phat products<br>See http://fullphat.net/redsquare/ for more details<br>'

    # build the http reply
    body = '<html><body>' + response + '</body></html>'
    reply = 'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(body)) + '\r\n\r\n' + body + '\r\n\r\n'

    # send it and close the socket
    print '[Info] Sending reply "' + response + '"...'
    conn.sendall(reply)
    conn.close()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# main()
#
print ''
print 'RedSquare ' + VERSION
print 'Copyright (c) 2016-2017 full phat products'

if len(sys.argv) > 1:
    if sys.argv[1] == '-?' or sys.argv[1] == '--help':
        print 'Usage: python RedSquare.py [port]'
        sys.exit()

    try:
        PORT = int(sys.argv[1])

    except:
        print '[Error] Invalid port specified: ' + sys.argv[1]
        sys.exit()

# install SIGINT signal handler
signal.signal(signal.SIGINT, signal_handler)

# load up our device handlers
get_handlers()

#b = rp_max7219lib.init()
#b = rp_nulllib.init()

# start listening
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    #print '  [Error] Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    print '[Error] Bind failed: you most likely already have something listening on port ' + str(PORT) 
    sys.exit()
     
s.listen(10)
print ""
print '[Info] Now listening for incoming requests on port ' + str(PORT)
print ""
 
# loop until we get a SIGINT...

while 1:
    # accept a connection
    conn, addr = s.accept()
    print '[Info] Connection made from ' + addr[0] + ':' + str(addr[1])
    thread = threading.Thread(target=client_thread, args=(conn,))
    thread.daemon = True
    thread.start()
