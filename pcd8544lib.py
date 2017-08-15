import time
import font

import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

from PIL import Image

def test():
	pass

def LCDinit():
	global disp
	global curX
	global curY

	# Raspberry Pi software SPI config:
	SCLK = 17
	DIN = 18
	DC = 27
	RST = 23
	CS = 22

	# Software SPI usage (defaults to bit-bang SPI interface):
	disp = LCD.PCD8544(DC, RST, SCLK, DIN, CS)

	# Initialize library.
	disp.begin(contrast=60)

	# Clear display.
	disp.clear()
	disp.display()
	curX = 0
	curY = 0

def LCDclearline(y):
	global disp

	buffer = disp.buffer()
	c = y*14*6
	for i in range(14*6):
		buffer[i+c] = 0


def LCDscrollup():
	global disp

	# one 'line' is 14 chars x 6 pixels...
	buffer = disp.buffer()
	for i in range((6-1)*(14*6)):
		buffer[i] = buffer[i + (14*6)]

#	disp.display()

def LCDnewline():
	global curX
	global curY
	curX = 0
	curY +=1
	if curY > 5:
		curY = 5
		LCDscrollup()
		LCDclearline(5)


# Display text (14 x 6 character screen)
def LCDprint(str):
	global disp
	global curX
	global curY

	if curY == 0 and curX == 0:
		blah = 0
	else:
		LCDnewline()

	buffer = disp.buffer()
	for a in str:
		if curX > 13:
			LCDnewline()

		i = ord(a)
		c = (i * 5)
		for b in range(5):
			# each character is 5 bytes (5x8)
			buffer[(curY*84) + (curX*6)+b] = font.font[c + b]

		curX += 1

	disp.display()

