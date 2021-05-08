#!/usr/bin/env python
"""TODO: DOCSTRING"""

from __future__ import print_function

import logging
import sys
import time
import pyautogui

from collections import namedtuple
from rtmidi.midiutil import open_midiinput

log = logging.getLogger('midiin_callback')
logging.basicConfig(level=logging.DEBUG)

DialMapping = namedtuple('DialMapping', ['increment', 'decrement'])


def get_dial_mappings():
    return [DialMapping('W', 'Q') for x in range(18)]


class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()
        self.dial_positions = {dial: 0 for dial in range(1,18)}
        self.dial_mappings = get_dial_mappings()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        if message[0] == 186:
            self.turn_dial_event(message[1], message[2])
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        print("%d, %d" % (message[1], message[2]))

    def turn_dial_event(self, dial, position):
        if dial == 9 or dial == 10:
            # Assign slider values
            self.dial_positions[9] = position
        else:
            if position <= self.dial_positions[dial]:
                key_press = self.dial_mappings[dial].increment
            else:
                key_press = self.dial_mappings[dial].decrement
            pyautogui.write(key_press*(self.dial_positions[9]+1))
            self.dial_positions[dial] = position


# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    midiin, port_name = open_midiinput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler(port_name))

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin
