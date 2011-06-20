DOTTED LANDSCAPE
================

Dotted Landscape aims to provide a LED control library built on
top of Python_ and Arduino_. Emphasis is on ease of use and extendability on 
all layers (plug in your code or hardware to the arduino, build software
modules on top of the python library, or create your own visuals through
a web frontend).

The software aims to invite people from different backgrounds to play with
the technology and come up with appropriate uses on their own.

Will work on Linux, probably on Mac, not likely on Windows.

.. _Python: http://www.python.org
.. _Arduino: http://www.arduino.cc


SERVER
------
blip_receiver.py - a class that understands the Blip-protocol from the Blinkenlights-project_
pygame_ledpanel.py - listens for incoming Blip-packets through BlipReceiver and visualizes
them with the help of PyGame-library_

.. _Blinkenlights-project: http://blinkenlights.net/
.. _PyGame-library: http://www.pygame.org/

Quick instructions:

#. Download the Blip-library from the Blinkenlights project to build a Blip-sender host or use your own.
#. Go to the server directory and run python pygame_ledpanel.py. It will start listening on all available interfaces
#. Run your Blip-sender (e.g. with the Blip-library: tests/test-movie-player movies/camel-18x8.blm 127.0.0.1)
#. Watch in awe as the camel moves on your screen


ARDUINO
-------
...