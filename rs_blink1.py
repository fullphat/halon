# RedSquare
# Blink(1) LED device library
# Copyright (c) 2017 full phat products
#
#
import threading
import struct
import time

Blink1 = None
devThread = None

def strobe(blink1, r, g, b, repeat):
	for i in range(repeat):
		blink1.fade_to_rgbn(0, r, g, b, 0)
		time.sleep(0.1)
		blink1.fade_to_rgbn(0, 0, 0, 0, 0)
		time.sleep(0.2)

def off(blink1):
	blink1.fade_to_rgbn(0, 0, 0, 0, 0)

def on(blink1, r, g, b):
	 blink1.fade_to_rgbn(0, r, g, b, 0)

def fade(blink1, r, g, b, delay):
	blink1.fade_to_rgbn(delay, r, g, b, 0)


def glimmer(blink1, r, g, b, repeat):
	fadems = 300
	waitms = (fadems + 50) / 1000.0

	for i in range(repeat):
		blink1.fade_to_rgbn(fadems, r, g, b, 1)
		blink1.fade_to_rgbn(fadems, int(r/2), int(g/2), int(b/2), 2)
		time.sleep(waitms)
		blink1.fade_to_rgbn(fadems, int(r/2), int(g/2), int(b/2), 1)
		blink1.fade_to_rgbn(fadems, r, g, b, 2)
		time.sleep(waitms)

	fade(blink1, 0, 0, 0, fadems)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# initialise - return True only if everything went ok
#
def init():

	global Blink1
	try:
		from support.blink1 import Blink1
		return True

	except Exception, e:
		print "[blink1]: couldn't load support library:", e
		return False

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# device handler
# return bool,string (True,"OK") if query was handled, or false otherwise
#
def handle(queryDict):

	# check to see if our thread is still running, if so
	# this means we're scrolling a message.  For now we
	# fail and return a 'device busy' message...

	# TO DO: look to see if we can queue messages

	global devThread
#	if maxThread:
#		if maxThread.is_alive():
#			print '[Info] device is busy - dropping this request...'
#			return (False, "Device is busy")

	# set defaults

	_unit = '0'
	_mode = 'glimmer'
	_rgb = 'ffffff'

	# get supplied info

	if 'unit' in queryDict:
		_unit = queryDict['unit'][0]

	if 'mode' in queryDict:
		_mode = queryDict['mode'][0]

	if 'rgb' in queryDict:
		_rgb = queryDict['rgb'][0]

#	if 'invert' in queryDict:
#		_invert = queryDict['invert'][0]

#	if 'font' in queryDict:
#		_font = queryDict['font'][0]

	# convert the text rgb into an r,g,b tuple...

	_rgb = _rgb.lstrip('#')
	if (len(_rgb) != 6):
		return (False, "Bad {rgb} value")

	try:
		r,g,b = struct.unpack('BBB', _rgb.decode('hex'))

	except:
		return (False, "Bad {rgb} value")

	if (r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255):
		return (False, "Bad {rgb} value")

	# start a thread to talk to the blink1

	devThread = threading.Thread(target=device_thread, args=(_unit, _mode, r, g, b))
	devThread.daemon = True
	devThread.start()
	return (True, "OK")

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# thread that talks to the blink(1)
#
def device_thread(unit, mode, red, green, blue):

	u = 0

	try:
		u = int(unit)

	except:
		print "[blink1]: invalid unit '" + unit + "'"
		return


	global Blink1
	device = Blink1(u)
	if (device.dev == None):
		print "[blink1]: no device found on unit #" + unit
		return

	print "[blink1] Unit #" + unit + ": Firmware  " + device.get_version()

	glimmer(device, red, green, blue, 6)

#	blink1.fade_to_rgb(1000, red, green, blue)
#	time.sleep(0.5)
#	blink1.fade_to_rgb(1000, 0, 0, 0)

