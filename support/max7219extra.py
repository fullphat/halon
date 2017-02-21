#!/usr/bin/env python

'''
This basic example shows use of the Python Pillow library:
sudo pip-3.2 install pillow # or sudo pip install pillow
Licensed under Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported License.
'''

#import signal
import time
#from sys import exit
#import sys

try:
	from PIL import Image

except ImportError:
	print 'Error loading PIL!'


import unicornhat as unicorn

def show_image(filename):
	img = Image.open(filename)
	for x in range(8):
		for y in range(8):
			pixel = img.getpixel((x,y))
			r, g, b = int(pixel[0]),int(pixel[1]),int(pixel[2])
			unicorn.set_pixel(x, y, r, g, b)
	unicorn.show()

def flash_image(statusIcon, imageIcon):
	for i in range(3):
		show_image('icons/' + statusIcon + '.png')
		time.sleep(1.0)
		show_image('icons/' + imageIcon + '.png')
		time.sleep(1.0)

unicorn.set_layout(unicorn.HAT)
unicorn.rotation(180)
unicorn.brightness(0.7)
flash_image(sys.argv[2], sys.argv[1])


