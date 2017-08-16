# RedSqaure
# unicornhathd.device handler
# this one uses the Pimoroni standard library and Pillow
# 16x16 16K RGB LED Matrix
# Copyright (c) 2017 full phat products
#

import threading
import time
import sos

maxThread = None
unicorn = None
Image = None
ImageFont = None
ImageDraw = None
queue = None

FONT = ("/usr/share/fonts/truetype/droid/DroidSans.ttf", 11)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# scroll_text(): scroll some text
#
def scroll_text(unicorn, text):

	if text == "":
		return

	width, height = unicorn.get_shape()
	text_x = width
	text_y = 2

	unicorn.rotation(90)


	global Image
	global ImageFont
	global ImageDraw
	global FONT

	# get the font...
	font_file, font_size = FONT
	font = ImageFont.truetype(font_file, font_size)

	#text_width, text_height = width, 0

	# determine text size...
	text_width, text_height = font.getsize(text)

	# create an 'empty' (black) bitmap to hold the text...
	text_width += width + text_x + 1
	image = Image.new("RGB", (text_width,max(16, text_height)), (0,0,0))
	draw = ImageDraw.Draw(image)
	offset_left = 0

	# draw the text into the bitmap...
	draw.text((text_x + offset_left, text_y), text, (255,255,255), font=font)
	offset_left += font.getsize(text)[0] + width

	for scroll in range(text_width - width):
		for x in range(width):
			for y in range(height):
				pixel = image.getpixel((x+scroll, y))
				r, g, b = [int(n) for n in pixel]
				unicorn.set_pixel(width-1-x, y, r, g, b)

		unicorn.show()
		time.sleep(0.01)

	unicorn.off()

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# show_image(): load and display the given image
#
def show_image(unicorn, filename):

	# load the pic...
	global Image
	img = Image.open(filename)
	width, height = unicorn.get_shape()

	unicorn.rotation(180)

	valid = False
	for x in range(width):
		for y in range(height):
			pixel = img.getpixel((y,x))
			r, g, b = int(pixel[0]),int(pixel[1]),int(pixel[2])
			if r or g or b:
				valid = True

			unicorn.set_pixel(x, y, r, g, b)

	if valid:
		unicorn.show()

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

	try:
		import unicornhathd as unicorn
		sos.sos_print("Got unicornhathd...'")

	except:
		sos.sos_fail("Couldn't load unicornhathd")
		sos.sos_print("To install the support library, see:")
		sos.sos_print("https://github.com/pimoroni/unicorn-hat-hd")
		return False

	try:
		from PIL import Image, ImageDraw, ImageFont
		sos.sos_print("Got Pillow...'")

	except:
		sos.sos_fail("Pillow not installed")
		sos.sos_print("Use 'sudo pip install pillow'")
		return False

	global queue
	queue = []

	# initialise the HAT
	sos.sos_print("Configuring device...")
	#unicorn.set_layout(unicorn.HAT)
	unicorn.brightness(1)
	show_image(unicorn, "./icons/save.png")
	time.sleep(0.5)
	unicorn.off()

	scroll_text(unicorn, "RSOS 2.21")

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
	mode = 'text'

	# special case: if 'mode=off' supplied, just turn off and exit

	if 'mode' in queryDict:
		mode = queryDict['mode'][0]

	if mode == 'off':
		unicorn.off()
		return (True, "Device turned off")

	elif mode == 'icon':
		# get supplied info
		priority = 0
		icon = ''
		if 'icon' in queryDict:
			icon = queryDict['icon'][0]

		# required elements...
		if icon == '':
			print '    [unicornhat]: no icon supplied!'
			return (False, "No icon provided")

#	if 'device' in queryDict:
#		_device = queryDict['device'][0]

	else:
		# assume mode is "text"...
		_font = ''
		_invert = '0'
		text = ''
		if 'text' in queryDict:
			text = queryDict['text'][0]

		if text != "":
			# good to go!
			sos.sos_print("Displaying '" + text + "'")
			scroll_text(unicorn, text)

		else:
			sos.sos_fail("No text to display")


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


