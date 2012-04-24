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

QUICKSTART
----------

  1. Download the code and install the dependencies
    - gEvent library: provides co-routines for the central server
    - Tornado web server: asynchronous communication for the web frontend
    - TornadIO2 addition: socket.io support for Tornado (NB: use v2)
    - Redis: database support for storing animations and usage statistics
    - on Linux (Debian variant) these steps might be completed with
      something like:

      $ sudo apt-get install python-dev python-setuptools libevent-dev && \
        sudo easy_install tornado tornadio2 gevent redis

  2. navigate into the src-directory

  3. start panel_server (python panel_server.py)
    - this starts the central panel server

  4. start the web frontend (python web_server.py)
    - this provides the web access to control the panel

  5. navigate to localhost:8888 to play around

  6. optionally start other components:
    - python osc_router.py to forward draw commands to Open Sound Control
    - python serial_connection.py to send commands via serial to something like an Arduino microcontroller
    - python pygame_ledpanel.py to show a quick panel that listens to any changes and displays them


CONNECTING BLINKENLIGHTS COMPONENTS
-----------------------------------

Unfortunately right now adding BL listeners is a bit harder. You need to hardcode them into
panel_server.py (just add to notify_clients). A command line switch needs to be added later.
