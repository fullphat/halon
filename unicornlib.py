# Generic unicorn library
# this one uses the Pimoroni standard library and Pillow
# Copyright (c) 2017 full phat products
#

import time
import sos

Image = None
ImageFont = None
ImageDraw = None


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# scroll_text(): scroll some text
#
# icon can be a full path or stock icon (if preceded with '!')
# Returns success(bool),hint(str)
#
def scroll_text(unicorn, rotationOffset, text, icon=""):

	if text == "":
		return False, "Nothing to display"

	hint = ""

	width, height = unicorn.get_shape()
	text_x = width
	text_y = 2

	# 8x8 hat is wired up differently... :-)
	if height == 8:
		unicorn.rotation(rotationOffset)
		text_y = 1

	else:
		unicorn.rotation(90)

	global Image
	global ImageFont
	global ImageDraw

	# get the font...

	if height == 8:
		FONT = ("/usr/share/fonts/truetype/droid/DroidSansMono.ttf", 7)
		#FONT = ("/usr/share/fonts/truetype/droid/DroidSans.ttf", 7)

	else:
		FONT = ("/usr/share/fonts/truetype/droid/DroidSans.ttf", 11)

	font_file, font_size = FONT
	font = ImageFont.truetype(font_file, font_size)

	# determine text size...
	text_width, text_height = font.getsize(text)
	text_width += width + text_x + 1

	# if an icon name is provided, load it...
	icn = None
	if icon != "":
		if icon[:1] == "!":
			iconpath = "./icons/" + str(height) + "/" + icon.lstrip('!') + ".png"

		else:
			iconpath = icon

		# try to load the icon...
		try:
			icn = Image.open(iconpath, 'r')

		except:
			hint = "Icon '" + iconpath + "' not found"

	# if the icon loaded ok, widen required bitmap...
	if icn != None:
		text_width += width + 2
		text_x += width + 2

	#print '***' + str(max(height,text_height))

	# create an 'empty' (black) bitmap to hold the text...
	image = Image.new("RGBA", (text_width,max(height, text_height)), (0,0,0,0))
	draw = ImageDraw.Draw(image)

	# draw the icon (if we have one)...
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
				if width == 8:
					# 8x8 hat is wired differently!
					unicorn.set_pixel(x, y, r, g, b)

				else:
					unicorn.set_pixel(width-1-x, y, r, g, b)


		unicorn.show()
		if height == 8:
			time.sleep(0.03)

		else:
			time.sleep(0.01)

	unicorn.off()
	return True, hint

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

