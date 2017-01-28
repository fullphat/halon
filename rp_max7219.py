# RedPowder ][
# MAX7219 8x8 LED Matrix device library
# Copyright (c) 2017 full phat products
#
#
import sys
import threading
import os

led = None 
maxThread = None

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# helper: retrieve the requested URL from a standard HTTP request
#
def init():
	global led
	try:
		import max7219.led as led
		from max7219.font import proportional, SINCLAIR_FONT, TINY_FONT, CP437_FONT
		return True

	except:
		print "[max7219]: couldn't load max7219.led"
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

	global maxThread
	if maxThread:
		if maxThread.is_alive():
			print '[Info] device is busy - dropping this request...'
			return (False, "Device is busy")

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

	maxThread = threading.Thread(target=device_thread, args=(_mode, _text, _invert, _font.lower()))
	maxThread.daemon = True
	maxThread.start()
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

