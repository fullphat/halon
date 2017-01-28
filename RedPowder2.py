# RedPowder ][
VERSION = "2.0"
# Copyright (c) full phat products
#
# Usage: python RedPowder.py [port]
#
# [port] will default to 6789 if not supplied
#
# Credit to binary tides for python threaded socket code
#
# 0.3: more helper functions added with a view to breaking code
#      up so we can better support different device types
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
    global libs
    try:
        lib = importlib.import_module(name, package=None)
        success = getattr(lib, 'init')()
        #print name + ":" + str(success)
        if success:
            libs[name] = lib

        else:
            print "[FAIL]: handler '" + name + "' loaded but didn't initialise"

    except:
        print "[FAIL]: handler '" + name + "' not found"


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# load up handlers - should be more dynamic (e.g. from
# a .conf file, or enumerating a directory)
#
def get_handlers():
    load_handler("rp_null")
    load_handler("rp_max7219")
    load_handler("rp_blink1")
    load_handler("xxx")			# test failure

    print libs

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
# v2 handler
# return bool,string (True,"OK") if query was handled, or
# false otherwise
#
def v2_handle(queryDict):
    global libs
    _device = ""

    if 'device' in queryDict:
        _device = queryDict['device'][0]

    try:
        dev = libs["rp_" + _device]
        if dev == None:
            print "[FAIL]: bad: " + _device
            return False, "bad device '" + _device + "'"

        # return the result of calling handler->handle()
        return getattr(dev, 'handle')(queryDict)

    except:
        print "[FAIL]: unknown device: " + _device
        return False, "Unknown device '" + _device + "'"

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
            # turn the query part into args
            d = parse_qs(o.query)
            #success,response = v1_handle(d)
            success = False
            response = "NEED TO REINSTATE V1 HANDLER"

        elif o.path == 'v2':
            d = parse_qs(o.query)
            success,response = v2_handle(d)

        else:
            print "[Error] invalid api version specified"
            response = 'Invalid API version specified'

    else:
        # null URL supplied - do we want to return hint/welcome message?
        print "[Warn] null path: returning our version info"
        response = 'RedPower ' + VERSION + '<br>Copyright (c) 2017 full phat products<br>'

    # build the http reply
    body = '<html><body>' + response + '</body></html>'
    reply = 'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(body)) + '\r\n\r\n' + body

    # send it and close the socket
    print '[Info] Sending reply "' + response + '"...'
    conn.sendall(reply)
    conn.close()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# main()
#
print ''
print 'RedPowder ' + VERSION
print 'Copyright (c) full phat products'

if len(sys.argv) > 1:
    if sys.argv[1] == '-?' or sys.argv[1] == '--help':
        print 'Usage: python RedPowder.py [port]'
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




s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    #print '  [Error] Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    print '[Error] Bind failed: you most likely already have something listening on port ' + str(PORT) 
    sys.exit()
     
s.listen(10)
print '[Info] Now listening for incoming requests on port ' + str(PORT)
 
# loop until we get a SIGINT...

while 1:
    # accept a connection
    conn, addr = s.accept()
    print '[Info] Connection made from ' + addr[0] + ':' + str(addr[1])
    thread = threading.Thread(target=client_thread, args=(conn,))
    thread.daemon = True
    thread.start()
