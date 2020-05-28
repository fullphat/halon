# Halon
# Blink(1) LED device library
# Copyright (c) 2018 full phat products
#
# Added support for V3 API
#

import threading
import struct
import time
import sos

import blink1lowlevel
from blink1support import DeviceInfo

Blink1 = None
Color = None

# list of blink1support->DeviceInfo objects
# initialised during init()
DeviceList = []




def rgb_from_string(rgb):

	r = -1
	g = -1
	b = -1
	success = False

	_rgb = rgb.lstrip('#')

	if (len(_rgb) == 6):
		try:
			r, g, b = struct.unpack('BBB', _rgb.decode('hex'))
			success = (r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255)

		except:
			sos.sos_fail("rgb_from_string: Bad {rgb} value")

	else:
		sos.sos_fail("rgb_from_string: Invalid rgb value (must be #rrggbb)")

	return (success, r, g, b)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# initialise - return True only if everything went ok
#
def init():

	global Blink1
	global Color

	try:
		from colour import Color

	except Exception, e:
		sos.sos_fail("Missing Colour library")
		sos.sos_info("Use '(sudo) pip install colour' to fix this")
		return False

	try:
		from support.blink1 import Blink1
		sos.sos_info("Got support library")

	except Exception, e:
		sos.sos_fail("Couldn't load support library:" + str(e))
		return False

	# run through available blink(1) devices

	sos.sos_print("Scanning for connected devices...")
	global Blink1
	for i in range(32):
		device = Blink1(i)
		if (device.dev != None):
			sos.sos_print("unit #" + str(i) + ": firmware " + device.get_version())

		else:
			break

	sos.sos_info("Scan complete")

	# did we find any devices?

	if i == 0:
		sos.sos_fail("No devices found!")
		return False

	# run the initialisation routine
	# for now, just cycle through the rainbow...

	for j in range(i):
		Blink1(j).fade_to_rgbn(100, 255, 0, 0, 0)
	time.sleep(0.1)

	for j in range(i):
		Blink1(j).fade_to_rgbn(100, 255, 255, 0, 0)
	time.sleep(0.1)

	for j in range(i):
		Blink1(j).fade_to_rgbn(100, 0, 255, 0, 0)
	time.sleep(0.1)

	for j in range(i):
		Blink1(j).fade_to_rgbn(100, 0, 255, 255, 0)
	time.sleep(0.1)

	for j in range(i):
		Blink1(j).fade_to_rgbn(100, 0, 0, 255, 0)
	time.sleep(0.1)

	for j in range(i):
		Blink1(j).fade_to_rgbn(100, 255, 0, 255, 0)
	time.sleep(0.1)

	for j in range(i):
		Blink1(j).fade_to_rgbn(100, 0, 0, 0, 0)

	sos.sos_print(str(i) + " device(s) found")
	sos.sos_print("Note that if you're using the V2 API, unit numbers must be doubled")

	# create a DeviceInfo object for each one found...

	global DeviceList
	for j in range(i):
		DeviceList.append(DeviceInfo())

	return True

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# v3 device handler
# return int,string,int (200,"OK",format) if query was handled
#   or false otherwise
#
# format is 0 (default) for JSON or 1 for raw
#
def handleNew(unit, command, queryDict, apiVersion):

#	print "[blink1] V3 API"
#	print command

	global DeviceList

	# validate unit number

	if (unit < -1 or unit > len(DeviceList)-1):
		sos.sos_fail("Invalid unit number #" + str(unit))
		return (400, "Invalid unit number specified")

	# broadcasting not done yet...

	if unit == -1:
		sos.sos_fail("Unit broadcast not yet implemented")
		return (501, "Unit broadcast not yet implemented")

	# request for info?

	sos.sos_info("Command=" + command)

	if command == "status":
		# return "ok", "0" or "1" and use raw format for now
		# formats: 0=json (default), 1=raw
		status = "1" if DeviceList[unit].IsOn() else "0"
		sos.sos_info("Status=" + status)
		return (200, status)

	elif command == "get":
		value = ""
		success = True

		# get current colour settings
		c = DeviceList[unit].Colour()

		typelist = queryDict.get("type", [])
		if "hue" in typelist:
			value = str(int(c.hue * 360))

		elif "saturation" in typelist:
			value = str(int(c.saturation * 100))

		elif "brightness" in typelist:
			value = str(int(c.luminance * 200))

		else:
			# return rgb value for now
			value = str(c.rgb)

		sos.sos_info("Value=" + value)
		return (200 if success else 404, value)

	# check to make sure we're not doing some asynchronous pattern...
	if DeviceList[unit].Thread():
		if DeviceList[unit].Thread().is_alive():
			sos.sos_fail("Unit #" + str(unit) + " is busy")
			return (409, "Requested unit is busy")

	r = 0
	g = 0
	b = 0
	r2 = 0
	g2 = 0
	b2 = 0

	if command == "off":
		if (setColourSync(Color("black"), unit)):
			DeviceList[unit].SetIsOn(False)
			return (200, "OK")

		else:
			return (400, "No device found on unit " + unit)

	elif command == "on":
		if (setColourSync(DeviceList[unit].Colour(), unit)):
			DeviceList[unit].SetIsOn(True)
			return (200, "OK")

		else:
			return (400, "No device found on unit " + unit)

	elif command == "set":
		# need two mandatory args: 'type' and 'value'
		typelist = queryDict.get("type", [])
		valuelist = queryDict.get("value", [])

		if len(typelist) == 0 or len(valuelist) == 0:
			return (400, "Missing required 'type' or 'value' parameter")

		if len(typelist) > 1 or len(valuelist) > 1:
			return (400, "Must specify only one 'type' and 'value' parameter")

		type = typelist[0]
		value = valuelist[0].replace("$", "#")

		sos.sos_info("Set " + type + " to " + value)

		# get the colour
		c = DeviceList[unit].Colour()

		if type == "hue":
			h = int(value) / 360.0
			c.hue = h

		elif type == "saturation":
			s = int(value) / 100.0
			c.saturation = s

		elif type == "brightness":
			b = int(value) / 200.0
			c.luminance = b

		elif type == "rgb":
			xc = Color(value)
			c.red = xc.red
			c.green = xc.green
			c.blue = xc.blue

		else:
			return (400, "Missing required parameter")

		# only update if the Blink(1) is on...
		if DeviceList[unit].IsOn():
			if (setColourSync(c, unit)):
				return (200, "OK")

			else:
				return (400, "No device found on unit " + unit)
		else:
			return (200, "OK")

	else:
		col1 = ""
		col2 = ""

		if 'rgb' in queryDict:
			col1 = queryDict['rgb'][0]
			col2 = col1

		if 'col1' in queryDict:
			col1 = queryDict['col1'][0]
			col2 = col1

		if 'col2' in queryDict:
			col2 = queryDict['col2'][0]

		# convert col1 into r,g,b...
		success, r, g, b = rgb_from_string(col1)
		if success == False:
			return (400, "Bad {col1} value: should be [#]rrggbb")

		# convert col2 into r,g,b...
		success, r2, g2, b2 = rgb_from_string(col2)
		if success == False:
			return (400, "Bad {col2} value: should be [#]rrggbb")


	# start a thread to talk to the blink1

	DeviceList[unit].Thread = threading.Thread(target=device_thread, args=(unit, command, r, g, b, r2, g2, b2))
	DeviceList[unit].Thread.daemon = True
	DeviceList[unit].Thread.start()
	return (200, "OK")


def setColourSync(c, unit):

	# get the r,g,b values...
	r = int(c.red * 255)
	g = int(c.green * 255)
	b = int(c.blue * 255)

	global Blink1
	device = Blink1(unit)
	if (device.dev == None):
		return False

	# set both LEDs immediately, and block until done...
	device.fade_to_rgbn(0, r, g, b, 1)
	device.fade_to_rgbn(0, r, g, b, 2)
	return True


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# device handler
# return bool,string (True,"OK") if query was handled, or false otherwise
#
def handle(queryDict, apiVersion=0, unit=0):

	u = 0

	if apiVersion == 2:
		# this will be the unit number * 2
		# to allow for support of dual LED devices
		u = unit // 2

	else:
		# validate unit number first
		_unit = '0'
		if 'unit' in queryDict:
			_unit = queryDict['unit'][0]

		try:
			u = int(_unit)

		except:
			sos.sos_fail("Invalid unit number #" + u)
			return (False, "Invalid unit number")

	# check the unit isn't busy (thread is running)

	global threadPool
	if threadPool[u]:
		if threadPool[u].is_alive():
			sos.sos_fail("Device #" + u + " is busy")
			return (False, "Device is busy")

	# decode supplied info

	_mode = 'glimmer'
	_rgb = 'ffffff'

	if 'mode' in queryDict:
		_mode = queryDict['mode'][0]

	if 'rgb' in queryDict:
		_rgb = queryDict['rgb'][0]

#	if 'invert' in queryDict:
#		_invert = queryDict['invert'][0]

#	if 'font' in queryDict:
#		_font = queryDict['font'][0]

	# convert the text rgb into an r,g,b tuple...

	_rgb = _rgb.lstrip('#')
	if (len(_rgb) != 6):
		return (False, "Bad {rgb} value")

	try:
		r,g,b = struct.unpack('BBB', _rgb.decode('hex'))

	except:
		return (False, "Bad {rgb} value")

	if (r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255):
		return (False, "Bad {rgb} value")

	# start a thread to talk to the blink1

	threadPool[u] = threading.Thread(target=device_thread, args=(u, _mode, r, g, b, r, g, b))
	threadPool[u].daemon = True
	threadPool[u].start()
	return (True, "OK")

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# thread that talks to the blink(1)
#
def device_thread(unitNum, command, red, green, blue, red2, green2, blue2):

	global Blink1
	device = Blink1(unitNum)
	if (device.dev == None):
		print "[blink1]: no device found on unit #" + unit
		return

	if command == "glimmer":
		glimmer(device, red, green, blue, 6, red2, green2, blue2)

	elif command == "flash":
		strobe(device, red, green, blue, red2, green2, blue2, 2)

	elif command == "strobe":
		strobe(device, red, green, blue, red2, green2, blue2, 6)

	elif command == "on":
		on(device, red, green, blue, red2, green2, blue2)

	elif command == "off":
		off(device)

	else:
		sos.sos_fail("Invalid command: " + command);



#	blink1.fade_to_rgb(1000, red, green, blue)
#	time.sleep(0.5)
#	blink1.fade_to_rgb(1000, 0, 0, 0)




#def strobe(blink1, r, g, b, r2, g2, b2, repeat):
#	for i in range(repeat):
#		blink1.fade_to_rgbn(0, r, g, b, 1)
#		blink1.fade_to_rgbn(0, r2, g2, b2, 2)
#		time.sleep(0.1)
#		blink1.fade_to_rgbn(0, 0, 0, 0, 0)
#		time.sleep(0.2)

#def off(blink1):
#	blink1.fade_to_rgbn(0, 0, 0, 0, 0)

#def on(blink1, r, g, b, r2=-1, g2=-1, b2=-1):

#	if r2 == -1:
#		r2 = r

#	if g2 == -1:
#		g2 = g

#	if b2 == -1:
#		b2 = b

#	blink1.fade_to_rgbn(0, r, g, b, 1)
#	blink1.fade_to_rgbn(0, r2, g2, b2, 2)

#def fade(blink1, r, g, b, delay, r2=-1, g2=-1, b2=-1, wait=0):

#	if r2 == -1:
#		r2 = r

#	if g2 == -1:
#		g2 = g

#	if b2 == -1:
#		b2 = b

#	blink1.fade_to_rgbn(delay, r, g, b, 1)
#	blink1.fade_to_rgbn(delay, r2, g2, b2, 2)

#	if wait > 0:
#		time.sleep(wait * 1000)
#		off(blink1)


#def glimmer(blink1, r, g, b, repeat, r2=-1, g2=-1, b2=-1):
#	fadems = 300
#	waitms = (fadems + 50) / 1000.0

#	if r2 == -1:
#		r2 = r

#	if g2 == -1:
#		g2 = g

#	if b2 == -1:
#		b2 = b

#	for i in range(repeat):
#		blink1.fade_to_rgbn(fadems, r, g, b, 1)
#		blink1.fade_to_rgbn(fadems, int(r2/2), int(g2/2), int(b2/2), 2)
#		time.sleep(waitms)
#		blink1.fade_to_rgbn(fadems, int(r/2), int(g/2), int(b/2), 1)
#		blink1.fade_to_rgbn(fadems, r2, g2, b2, 2)
#		time.sleep(waitms)

#	fade(blink1, 0, 0, 0, fadems)
