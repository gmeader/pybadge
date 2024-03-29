# pyBadge & PyGamer
### Some examples of CircuitPython code for the Adafruit PyBadge and PyGamer

PyBadge and PyGamer are products from <a href="http://adafruit.com">adafruit.com</a> They are tiny inexpensive ($50) hand-held computers with a color LCD and buttons/joystick. They can do USB MIDI. You can plug a board called MIDI Featherwing into these computers to add 5-pin DIN MIDI In and Out jacks. 

* buttons.py is a simple demo that shows which PyBadge buttons are pressed
* midiclock is an app that displays MIDI clock status on the USB MIDI connection to a host
* MIDImatrix folder contains a graphical display of received MIDI from a MIDI Featherwing - Video demo: https://www.youtube.com/watch?v=8wvDsd-fElc
* metronome.py is a musician's tool with graphics display controlled by buttons on PyBadge - Video demo: https://www.youtube.com/watch?v=ICGBr8tG5b0&t=4s
* joystick_long is Arduino code for a demo of detecting long and short button presses on PyBadge (not CircuitPython)
* writefiles is an example of how to make the PyBadge filesystem writeable
* uart_midi folder contains code that works with the MIDI Featherwing plugged into the Pybadge & PyGamer, also an example that uses both USB and UART MIDI ports
* MIDIcommander.py - A "patch librarian" that stores MIDI SYSEX files (or .mic files that can contain any MIDI command byte strings) on the SDcard; plays them out the MIDI Featherwing MIDI Out port at the push of a button. Uses the joystick to navigate folders of files from the SDcard on the LCD display. Runs only on PyGamer, as the SDcard is required. Video demo: https://youtu.be/xjDKXFzHlWw

# PyGamer folder
* pygamer/controls.py - Simple CircuitPython test of PyGamer buttons and joystick events


