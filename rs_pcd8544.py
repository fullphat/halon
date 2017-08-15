# RedSqaure
# pcd8544.device handler
# LCD matrix used in the original Nokia 3310 phones
# Copyright (c) 2017 full phat products
#
import threading
import sos

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# init: 
#
def init():
	global lcd

	try:
		import pcd8544lib as lcd
                sos.sos_print("Initialising device...")
		lcd.LCDinit()
                lcd.LCDprint("RSOS 2.1")
                lcd.LCDprint("READY")
		return True

	except:
		sos.sos_fail("Couldn't load pcd8544lib")
		return False

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# device handler
# return bool,string (True,"OK") if query was handled, or false otherwise
#
def handle(queryDict, apiVersion=0, unit=0):

	# check to see if our thread is still running, if so
	# this means we're scrolling a message.  For now we
	# fail and return a 'device busy' message...

	# get supplied info...

	if 'device' in queryDict:
		_device = queryDict['device'][0]

	if 'mode' in queryDict:
		_mode = queryDict['mode'][0]

	if 'text' in queryDict:
		_text = queryDict['text'][0]


	# final checks...

	if _text == "":
		return (False, "Nothing to display")

	sos.sos_print("Unit is " + str(unit))

	lcd.LCDprint(_text)
	return (True, "OK")

