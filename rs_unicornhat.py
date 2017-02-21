# RedSqaure
# unicornhat.device handler
# this one uses the Pimoroni standard library and Pillow
# 8x8 16K RGB LED Matrix
# Copyright (c) 2017 full phat products
#
import threading
import time

maxThread = None
unicorn = None
Image = None

queue = None

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# show_image(): load and display the given 8x8 image
#
def show_image(unicorn, filename):
	global Image
	img = Image.open(filename)
	for x in range(8):
		for y in range(8):
			pixel = img.getpixel((x,y))
			r, g, b = int(pixel[0]),int(pixel[1]),int(pixel[2])
			unicorn.set_pixel(x, y, r, g, b)
	unicorn.show()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# flash: alternate between the two given 8x8 images
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

	try:
		import unicornhat as unicorn
		print "    [unicornhat]: Got unicornhat...'"

	except:
		print "    [unicornhat]: Couldn't load unicornhat!"
		return False

	try:
		from PIL import Image
		print "    [unicornhat]: Got Pillow...'"

	except:
		print "    [unicornhat]: Pillow not installed.  Use 'sudo pip install pillow'"
		return False

	global queue
	queue = []

	# initialise the HAT

	print "    [unicornhat]: Configuring device..."
	print "    [unicornhat]: [TBD: should load these settings from unicornhat.rc]"
	unicorn.set_layout(unicorn.HAT)
	unicorn.rotation(180)
	unicorn.brightness(0.4)
	return True

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# device handler
# return bool,string (True,"OK") if query was handled, or false otherwise
#
def handle(queryDict):

	# queue the request...

	global queue
	queue.append(queryDict)

	global maxThread
	if maxThread:
		if maxThread.is_alive():
			print '    [unicornhat] busy: added to queue...'
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

	# set defaults

	_device = '0'
	_mode = 'scroll'

	# special case: if 'mode=off' supplied, just turn off and exit

	if 'mode' in queryDict:
		_mode = queryDict['mode'][0]

	if _mode == 'off':
		unicorn.off()
		return (True, "Device turned off")



	_priority = 0
	_icon = ''

	# get supplied info

#	if 'device' in queryDict:
#		_device = queryDict['device'][0]

	if 'icon' in queryDict:
		_icon = queryDict['icon'][0]

	# required elements...

	if _icon == '':
		print '    [unicornhat]: no icon supplied!'
		return (False, "No icon provided")

	# optional elements...

	_font = ''
	_text = ''
	_invert = '0'





#	if 'text' in queryDict:
#		_text = queryDict['text'][0]

#	if 'invert' in queryDict:
#		_invert = queryDict['invert'][0]

#	if 'font' in queryDict:
#		_font = queryDict['font'][0]

	if 'priority' in queryDict:
		_priority = queryDict['priority'][0]

	# determine status icon to use

	pri = 0
	try:
		pri = int(_priority)

	except:
		print '    [unicornhat]: bad priority: ' + _priority

	if pri > 1:
		_statusIcon = 'alert'

	elif pri == 1:
		_statusIcon = 'warn'

	else:
		_statusIcon = 'info'


	# good to go!

	flash_image(unicorn, _statusIcon, _icon)

#	if _text == "":
#		return (False, "Nothing to display")


