# RedSqaure
# unicornhathd.device handler
# this one uses the Pimoroni standard library and Pillow
# 16x16 16K RGB LED Matrix
# Copyright (c) 2017 full phat products
#

import threading
import time
import sos

BOOT_ICON = "thing-color_wheel"
BOOT_VER = "2.47"

unicorn = None
unicornLib = None

# number of concurrent threads (matches detected devices)
maxThread = None

# list of queued requests
queue = None



#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# flash: alternate between the two given images
#
def flash_image(unicorn, statusIcon, imageIcon, repeat=3):
	for i in range(repeat):
		show_image(unicorn, 'icons/' + statusIcon + '.png')
		time.sleep(1.0)
		show_image(unicorn, 'icons/' + imageIcon + '.png')
		time.sleep(1.0)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# init: try to load up luma.led_matrix
#
def init():
	global unicorn
	global Image
	global ImageDraw
	global ImageFont

	global unicornlib

	try:
		import unicornlib
		sos.sos_print("Got unicornlib...'")

	except:
		sos.sos_fail("Couldn't load unicornlib")
		return False

	try:
		import unicornhathd as unicorn
		sos.sos_print("Got unicornhathd...'")

	except:
		sos.sos_fail("Couldn't load unicornhathd")
		sos.sos_print("To install the support library, see:")
		sos.sos_print("https://github.com/pimoroni/unicorn-hat-hd")
		return False


	global queue
	queue = []

	# initialise the HAT
	sos.sos_print("Configuring device...")
	#unicorn.set_layout(unicorn.HAT)
	unicorn.brightness(1)
	#show_image(unicorn, "./icons/save.png")
	#time.sleep(0.5)
	unicorn.off()

	unicornlib.scroll_text(unicorn, 90, "RSOS " + BOOT_VER, "!" + BOOT_ICON)

	return True

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# device handler
# return bool,string (True,"OK") if query was handled, or false otherwise
#
def handle(queryDict, apiVersion=0, unit=0):

	# queue the request...
	global queue
	queue.append(queryDict)

	global maxThread
	if maxThread:
		if maxThread.is_alive():
			sos.sos_info('Device is busy, request added to queue')
			return (True, "Request queued")

	# start a thread to display the message

	#maxThread = threading.Thread(target=device_thread, args=(queryDict,))
	maxThread = threading.Thread(target=device_thread)
	maxThread.daemon = True
	maxThread.start()
	return (True, "OK")


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# thread that talks to the unicornhat
#
def device_thread():

	global queue

	while len(queue) > 0:
		# pop from top of list
		dict = queue[0]
		del queue[0]
		# process it
		process(dict)



#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# thread that talks to the unicornhat
#
def process(queryDict):

	global unicorn
	global unicornlib

	# set defaults

	_device = '0'
	mode = 'text'
	icon = ''

	# read variables...

	if 'icon' in queryDict:
		icon = queryDict['icon'][0]

	if 'mode' in queryDict:
		mode = queryDict['mode'][0]


	# process based on mode...

	if mode == "off":
		unicorn.off()
		return (True, "Device turned off")

	elif mode == "icon":
		# get supplied info
		priority = 0

		# required elements...
		if icon == '':
			print '    [unicornhat]: no icon supplied!'
			return (False, "No icon provided")

#	if 'device' in queryDict:
#		_device = queryDict['device'][0]

	elif mode == "text":
		_font = ''
		_invert = '0'
		text = ''
		if 'text' in queryDict:
			text = queryDict['text'][0]

		if text != "":
			# good to go!
			p = 0

			if icon == "":
				if 'priority' in queryDict:
					try:
						p = int(queryDict['priority'][0])

					except:
						sos.sos_warn("Invalid priority specified")

				if p == 1:
					# high
					icon = "system-warning"

				elif p > 1:
					# urgent
					icon = "system-urgent"

				else:
					# info
					icon = "system-info"

			sos.sos_print("Displaying '" + text + "'")
			result,hint = unicornlib.scroll_text(unicorn, 90, text, icon)
			if hint != "":
				sos.sos_warn("scroll_text(): " + hint)
		else:
			sos.sos_fail("No text to display")
			return (False, "Nothing to do")

	return (True, "OK")


#	if 'invert' in queryDict:
#		_invert = queryDict['invert'][0]
#	if 'font' in queryDict:
#		_font = queryDict['font'][0]

#	if 'priority' in queryDict:
#		_priority = queryDict['priority'][0]

	# determine status icon to use

#	pri = 0
#	try:
#		pri = int(_priority)

#	except:
#		print '    [unicornhat]: bad priority: ' + _priority

#	if pri > 1:
#		_statusIcon = 'alert'

#	elif pri == 1:
#		_statusIcon = 'warn'

#	else:
#		_statusIcon = 'info'


	# good to go!

#	flash_image(unicorn, _statusIcon, _icon)

#	if _text == "":
#		return (False, "Nothing to display")

if __name__ == '__main__':
	init()


