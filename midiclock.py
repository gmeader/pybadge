# for Adafruit PyBadge
# display MIDI clock as BPM with start and stop commads
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

font = bitmap_font.load_font("fonts/Helvetica-Bold-16.bdf")
#font = terminalio.FONT

title = label.Label(font, text="Midi Clock Monitor", color=0x008000)
# Set the location
title.x = 5
title.y = 20
group.append(title)

info = label.Label(font, text=" no clock ", color=0xFFFF00)
info.x = 46
info.y = 68
group.append(info)

cmd = label.Label(font, text="          ", color=0xFF8000)
cmd.x = 55
cmd.y = 110
group.append(cmd)

display.show(group)

midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel="ALL")

print("Midi Clock Monitor 1.0")

ticks = 0
start = time.monotonic()

while True:
    #for pause in pauses:
        msg = midi.receive()
        if msg is not None:

            if isinstance(msg, TimingClock):
                ticks +=1
                if ticks == 24: # midi clock is 24 ticks per beat
                    beat_time = float(time.monotonic()-start)
                    bpm = str(math.floor(60/beat_time))
                    start = time.monotonic()
                    ticks = 0
                    info.text = bpm + " BPM  "
            if isinstance(msg, Start):
                print( 'start' )
                cmd.text = 'Start '
            if isinstance(msg, Stop):
                print('stop' )
                cmd.text = 'Stop  '