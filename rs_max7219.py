# RedSqaure
# max7219.device handler
# 8x8 LED Matrix
# Copyright (c) 2017 full phat products
#
#import sys
import threading
#import os

led = None 
maxThread = None

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# init: try to load up luma.led_matrix
#
def init():
	global legacy
	global max7219
	global spi
	global noop

	try:

		from luma.led_matrix import legacy
		from luma.led_matrix.device import max7219
		from luma.core.serial import spi, noop
		return True

	except:
		print "[max7219]: couldn't load luma.led_matrix"
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

	serial = spi(port=0, device=0, gpio=noop())
	device = max7219(serial, cascaded=1, block_orientation="horizontal")
	print("Created device")

	# default font is CP437
	font = legacy.proportional(legacy.CP437_FONT)

	if fontName == "sinclair":
		font = legacy.proportional(legacy.SINCLAIR_FONT)

	elif fontName == "tiny":
		font = legacy.proportional(legacy.TINY_FONT)

	legacy.show_message(device, text, fill="white", font=font)

