# RedPowder ][
# Blink(1) LED device library
# Copyright (c) 2017 full phat products
#
#
#import sys
import threading
#import os
import time

blink1 = None 
#maxThread = None

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
	global blink1
	try:
		from blink1_pyusb import Blink1 as Blink1
		blink1 = Blink1()
		if blink1.dev == None:
			print "[blink1]: no device found"
			return False

		else:
			return True

	except:
		print "[blink1]: couldn't load "
		return False

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# device handler
# return bool,string (True,"OK") if query was handled, or false otherwise
#
def handle(queryDict):

	global blink1
	glimmer(blink1, 255, 255, 255, 6)

	# check to see if our thread is still running, if so
	# this means we're scrolling a message.  For now we
	# fail and return a 'device busy' message...

	# TO DO: look to see if we can queue messages

#	global maxThread
#	if maxThread:
#		if maxThread.is_alive():
#			print '[Info] device is busy - dropping this request...'
#			return (False, "Device is busy")

	# set defaults

	_device = '0'
	_mode = 'scroll'
	_font = ''
	_text = ''
	_invert = '0'

	# get supplied info

	if 'device' in queryDict:
		_device = queryDict['device'][0]

	if 'mode' in queryDict:
		_mode = queryDict['mode'][0]

	if 'text' in queryDict:
		_text = queryDict['text'][0]

	if 'invert' in queryDict:
		_invert = queryDict['invert'][0]

	if 'font' in queryDict:
		_font = queryDict['font'][0]


	if _text == "":
		return (False, "Nothing to display")

	# start a thread to display the message

#	maxThread = threading.Thread(target=device_thread, args=(_mode, _text, _invert, _font.lower()))
#	maxThread.daemon = True
#	maxThread.start()
	return (True, "OK")

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# thread that talks to the max7219
#
def device_thread(mode, text, invert, fontName):
	matrix = led.matrix(cascaded=1)

	if invert == "1":
		matrix.invert(True)

	# default font is CP437
	font = proportional(CP437_FONT)

	if fontName == "sinclair":
		font = proportional(SINCLAIR_FONT)

	elif fontName == "tiny":
		font = proportional(TINY_FONT)

	# mode

	if mode == "print":
		chr = text[0]
		matrix.letter(0, ord(chr), font, False)
		matrix.scroll_right()
#        device.flush()

	else:
		matrix.show_message(text, font)
		matrix.clear()

