# Halon

## Synopsis

Python-based micro webserver that controls various LED matricies, LCD displays, LEDs and other nifty widgets in a structured, easily-accessible, and extensible way.

## Concept

Halon provides a modular platform based on a single central webserver, a standard helper library and any number of third-party-created device modules that interface with varying physical devices.

Typically this will be a Raspberry Pi or similar system although, so long as the system supports Python 2.7, TCP sockets, and has the appropriate support libraries installed, it should work anywhere.

## Supported Devices

- Max7219 8x8 LED Matrix
- Thingm Blink(1) USB LED
- Pimoroni UnicornHAT and UnicornHAT HD

## Support Planned

- Nokia 3310/5110 LCD Display
- Pimoroni pHAT

## Examples

The following examples use **curl**, however you could just paste everything but "curl" into the address bar of your favourite browser.  Don't forget to prefix with "http://" of course.

Display "Hello world!" as a scrolling message on a MAX7219 8x8 Matrix:

```curl 127.0.0.1:6789/v1?device=max7219&text=Hello%20world%21```

Glimmer the second Blink(1) device connected to your system a nice shade of magenta:

```curl 127.0.0.1:6789/v1?device=blink1&unit=1&mode=glimmer&rgb=ff00ff```

## Getting Started

(This is just some quick notes; a better guide will follow)

* Clone this repository

* Launch Halon:

`sudo python halon.py`

Note that Halon runs under Python 2.7 at the moment.  You may be able to run Halon without `sudo`, it depends on which devices you're intending to use.  Blink(1) devices require `sudo` as Halon needs access to the USB ports.

## Troubleshooting

If you find your devices aren't detected, or you see errors when launching Halon, check the following:

- You're using a Raspberry Pi.  Halon should work on other platforms, but it's only been tested on a Pi.
- You have Python 2.7 installed.  This is almost a given, but it's worth checking.
- You have required supporting libraries installed.  See the following for specifics:

### UnicornHAT HD

You should see a message scroll across the HAT during Halon startup.  If not, check you've installed the helper libraries already:

'curl https://get.pimoroni.com/unicornhathd | bash'

More details here: https://github.com/pimoroni/unicorn-hat-hd

### Blink(1)

Any connected Blink(1) devices should cycle through a rainbow scheme during startup.  If not:

- Check the Blink(1) devices flash briefly when your computer powers on

- Check you've installed PyUSB:

`sudo pip install pyusb`

- Check you've installed colour 0.1.5 (or later):

`sudo pip install colour`

More details here: https://github.com/todbot/blink1-python
