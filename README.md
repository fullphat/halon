# RedSquare

A Python-based micro web server that controls various light widgets.

## Concept

RedSquare provides a simple web server that abstracts the different libraries required to talk to the various different widgets.  Support is designed to be seamless, so if you don't have a particular widget, RedSquare will fail gracefully.

## Supported Devices

- Max7219 8x8 LED Matrix
- Thingm Blink(1) USB LED

## Supported Planned

- Nokia 3310/5110 LCD Display
- Pimoroni HAT (and pHAT)

## Examples

The following examples use *curl*, however you could just paste everything after "curl" into the address bar of your favourite browser.  Don't forget to prefix with "http://" of course.

Display "Hello world!" as a scrolling message on a MAX7219 8x8 Matrix:

'''curl 127.0.0.1:6789/v1?device=max7219&text=Hello%20world%21'''

Glimmer the second Blink(1) device connected to your system a nice shade of magenta:

'''curl 127.0.0.1:6789/v1?device=blink1&unit=1&mode=glimmer&rgb=ff00ff'''





