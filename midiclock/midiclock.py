# CircuitPython for Adafruit PyBadge
# display received MIDI clock messages as BPM
# and MIDI clock start and stop commands
import time
import math
import board
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import usb_midi
import adafruit_midi
from adafruit_midi.timing_clock            import TimingClock
from adafruit_midi.start                   import Start
from adafruit_midi.stop                    import Stop

display = board.DISPLAY
group = displayio.Group()
font = bitmap_font.load_font("fonts/Helvetica-Bold-16.bdf") #optional: font = terminalio.FONT

#Draw the display screen
lbl_title = label.Label(font, text="Midi Clock Monitor", color=0x008000)
# Set the location
lbl_title.x = 5
lbl_title.y = 20
group.append(lbl_title)

lbl_info = label.Label(font, text=" no clock            ", color=0xFFFF00)
lbl_info.x = 46
lbl_info.y = 68
group.append(lbl_info)

lbl_cmd = label.Label(font, text="          ", color=0xFF8000)
lbl_cmd.x = 55
lbl_cmd.y = 110
group.append(lbl_cmd)

display.show(group)

#start receiving MIDI messages from USB, any MIDI channel
midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel="ALL")

print("Midi Clock Monitor 1.0")

ticks = 0
start = time.monotonic() # start the timer to measure clock ticks

while True:
    msg = midi.receive()

    if msg is not None:
        if isinstance(msg, TimingClock): # receive a MIDI tick message
            ticks +=1
            if ticks == 24: # midi clock is 24 ticks per beat
                beat_time = float(time.monotonic()-start)
                bpm = str(math.floor(60/beat_time))
                # reset the timer, to start measuring the next beat
                start = time.monotonic()
                ticks = 0
                lbl_info.text = bpm + " BPM  "
        # display Start or Stop message has been received
        if isinstance(msg, Start):
            print( 'start' )
            lbl_cmd.text = 'Start '
        if isinstance(msg, Stop):
            print('stop' )
            lbl_cmd.text = 'Stop  '
        '''
        # not implemented in library yet
        if isinstance(msg, Continue):
            print('continue' )
            lbl_cmd.text = 'Continue'
        '''
    else:
        if time.monotonic()-start > 2: # no MIDI messages received in the last 2 sec
            lbl_info.text = ' no clock '  
            start = time.monotonic()      
