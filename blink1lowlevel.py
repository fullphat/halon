# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Blink(1) LED device low level functions
# Copyright (c) 2020 full phat products
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#
# Flash the specified device quickly, imitating a strobe effect
# r,g,b = colour to strobe
# repeat = number of times to strobe
#
def strobe(blink1, r, g, b, r2, g2, b2, repeat):
	for i in range(repeat):
		blink1.fade_to_rgbn(0, r, g, b, 1)
		blink1.fade_to_rgbn(0, r2, g2, b2, 2)
		time.sleep(0.1)
		blink1.fade_to_rgbn(0, 0, 0, 0, 0)
		time.sleep(0.2)

#
# Turn the specified device off
#
def off(blink1):
	blink1.fade_to_rgbn(0, 0, 0, 0, 0)

#
# Set the specified device to a particular rgb value
# r,g,b     colour to set LED 1 to
# r2,g2,b2  colour to set LED 2 to (if not specified, then r,g,b is used)
#
def on(blink1, r, g, b, r2=-1, g2=-1, b2=-1):

	if r2 == -1:
		r2 = r

	if g2 == -1:
		g2 = g

	if b2 == -1:
		b2 = b

	blink1.fade_to_rgbn(0, r, g, b, 1)
	blink1.fade_to_rgbn(0, r2, g2, b2, 2)

def fade(blink1, r, g, b, delay, r2=-1, g2=-1, b2=-1, wait=0):

	if r2 == -1:
		r2 = r

	if g2 == -1:
		g2 = g

	if b2 == -1:
		b2 = b

	blink1.fade_to_rgbn(delay, r, g, b, 1)
	blink1.fade_to_rgbn(delay, r2, g2, b2, 2)

	if wait > 0:
		time.sleep(wait * 1000)
		off(blink1)


def glimmer(blink1, r, g, b, repeat, r2=-1, g2=-1, b2=-1):
	fadems = 300
	waitms = (fadems + 50) / 1000.0

	if r2 == -1:
		r2 = r

	if g2 == -1:
		g2 = g

	if b2 == -1:
		b2 = b

	for i in range(repeat):
		blink1.fade_to_rgbn(fadems, r, g, b, 1)
		blink1.fade_to_rgbn(fadems, int(r2/2), int(g2/2), int(b2/2), 2)
		time.sleep(waitms)
		blink1.fade_to_rgbn(fadems, int(r/2), int(g/2), int(b/2), 1)
		blink1.fade_to_rgbn(fadems, r2, g2, b2, 2)
		time.sleep(waitms)

	fade(blink1, 0, 0, 0, fadems)
