# RedSquare

A Python-based micro web server that controls various light widgets.

The idea is that you use a standard URL request to talk to the different widgets and RedSquare handles the actual communications.

## Currently supported:

- Max7219 8x8 LED Matrix
- Thingm Blink(1) USB LED

## Examples

curl 127.0.0.1:6789/v1?device=max7219&text=Hello%20world%21

Displays "Hello world!" as a scrolling message on a MAX7219 8x8 Matrix

curl 127.0.0.1:6789/v1?device=blink1&unit=1&mode=glimmer&rgb=ff00ff

Glimmers the second Blink(1) device connected to your system a nice shade of magenta.



