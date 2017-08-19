# Generic unicorn library
# this one uses the Pimoroni standard library and Pillow
# Copyright (c) 2017 full phat products
#

import time
import sos

Image = None
ImageFont = None
ImageDraw = None

FONT = ("/usr/share/fonts/truetype/droid/DroidSans.ttf", 11)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# scroll_text(): scroll some text
#
def scroll_text(unicorn, text, icon=""):

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

	# determine text size...
	text_width, text_height = font.getsize(text)
	text_width += width + text_x + 1

	# if an icon name is provided, load it...
	icn = None
	if icon != "":
		try:
			icn = Image.open('./icons/' + str(height) + '/' + icon + '.png', 'r')

		except:
			pass

	# if the icon loaded ok, widen required bitmap...
	if icn != None:
		text_width += width + 2
		text_x += width + 2

	# create an 'empty' (black) bitmap to hold the text...
	image = Image.new("RGBA", (text_width,max(height, text_height)), (0,0,0,0))
	draw = ImageDraw.Draw(image)

	# draw the icon (if provided)...
	if icn != None:
		image.paste(icn, (width,0), icn)

	# draw the text into the bitmap...
	draw.text((text_x, text_y), text, (255,255,255), font=font)
	#offset_left += font.getsize(text)[0] + width

	for scroll in range(text_width - width):
		for x in range(width):
			for y in range(height):
				pixel = image.getpixel((x+scroll, y))
				r, g, b, a = [int(n) for n in pixel]
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


def init():

	global Image
	global ImageDraw
	global ImageFont

        try:
                from PIL import Image, ImageDraw, ImageFont
                sos.sos_print("Got Pillow...")

        except:
                sos.sos_fail("Pillow not installed")
                sos.sos_print("Use 'sudo pip install pillow'")
                return False

init()

