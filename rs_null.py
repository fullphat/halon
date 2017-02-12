# RedSquare
# null.device handler
# Copyright (c) 2017 full phat products
#
# Just prints to stdout - handy for testing
#
#import sys


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# initialisation: return True if loaded ok, False otherwise
#
def init():
	return True

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# device handler
# return bool,string (True,"OK") if query was handled, or false otherwise
#
def handle(queryDict):

	# print queryDict

	# set defaults

	_text = ''

	# get supplied info

	if 'text' in queryDict:
		_text = queryDict['text'][0]

	print "[null.device]: " + _text
	return (True, "OK")

