	
"""
'metronome.py'.
for AdaFruit PyBadge
CircuitPython
Glenn Meader 2020


"""
import time
import board
import simpleio
import digitalio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from gamepadshift import GamePadShift
pad = GamePadShift(digitalio.DigitalInOut(board.BUTTON_CLOCK),
                   digitalio.DigitalInOut(board.BUTTON_OUT),
                   digitalio.DigitalInOut(board.BUTTON_LATCH))

# pybadge buttons
BUTTON_LEFT = const(128)
BUTTON_UP = const(64)
BUTTON_DOWN = const(32)
BUTTON_RIGHT = const(16)
BUTTON_SEL = const(8)
BUTTON_START = const(4)
BUTTON_A = const(2)
BUTTON_B = const(1)

play = True
beats_per_measure = 4
accent = True
view_help = False

display = board.DISPLAY
font = terminalio.FONT
bigfont = bitmap_font.load_font("fonts/Helvetica-Bold-16.bdf")

window = displayio.Group(max_size=5) # group to contain 2 view groups


main_view = displayio.Group(max_size=10)

title = label.Label(bigfont, text="Metronome", color=0x008000)
title.x = 38
title.y = 20
main_view.append(title)

lbl_beat = label.Label(bigfont, text=" BEAT ", color=0xFFFF00)
lbl_beat.x = 80
lbl_beat.y = 46
main_view.append(lbl_beat)

lbl_bpm = label.Label(bigfont, text="      BPM ", color=0xC08000)
lbl_bpm.x = 20
lbl_bpm.y = 70
main_view.append(lbl_bpm)

lbl_beats = label.Label(bigfont, text=str(beats_per_measure)+"/4", color=0xC04000)
lbl_beats.x = 110
lbl_beats.y = 70
main_view.append(lbl_beats)

lbl_info = label.Label(font, text="   Press B for HELP                          ", color=0xA0A0A0)
lbl_info.x = 10
lbl_info.y = 110
main_view.append(lbl_info)


help_view = displayio.Group()
lbl_help = label.Label(font, line_spacing=1.0, text='''     HELP = press B\n
Change BPM with pad
  Up/Down/L/R buttons
START to pause/play
SELECT to change
  beats per measure
A to toggle accent
  on first beat''', color=0xFFFFFF)
lbl_help.x = 5
lbl_help.y = 65
help_view.append(lbl_help)

#sow the main view
window.append(main_view)
display.show(window)

# enable the pybadge speaker
speakerEnable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
speakerEnable.switch_to_output(value=True)

def display_bpm(bpm):
    lbl_bpm.text=str(bpm) + ' BPM'

def check_buttons(buttons):
    global bpm
    if (buttons & BUTTON_RIGHT) > 0:
        bpm += 1
        display_bpm(bpm)
        return 'RIGHT'
    elif (buttons & BUTTON_LEFT) > 0:
        bpm -= 1
        display_bpm(bpm)
        return 'LEFT'
    elif (buttons & BUTTON_UP) > 0:
        bpm += 10
        display_bpm(bpm)
        return 'UP'
    elif (buttons & BUTTON_DOWN) > 0:
        bpm -= 10
        display_bpm(bpm)
        return 'DOWN'
    elif (buttons & BUTTON_A) > 0:
        toggle_accent()
        return 'A'
    elif (buttons & BUTTON_B) > 0:
        toggle_help()
        return 'B'
    elif (buttons & BUTTON_SEL) > 0:
        set_beats()
        return 'SELECT'
    elif (buttons & BUTTON_START) > 0:
        toggle_play()
        return 'START'
         
def get_buttons():
    # check to see if any buttons are pressed
    buttons = pad.get_pressed()
    if buttons != 0:
    	time.sleep(0.05)  # wait debounce time
    	next_buttons = pad.get_pressed() 
    	if buttons == next_buttons: #is same button still pressed?
            check_buttons(buttons)
            time.sleep(0.1) # don't allow clicking buttons too fast

def toggle_play():
    global play
    global lbl_info
    play = not play
    if play:
        lbl_info.text = "Press START to pause\n B for HELP"
    else:
        lbl_info.text = "        PAUSED\nPress START to play"
        
def toggle_accent():
    global accent
    global lbl_info
    accent = not accent
    if accent:
        lbl_info.text = "Accent on first beat"
    else:
        lbl_info.text = "No accent on first beat"
    
def toggle_help():
    global view_help
    view_help = not view_help
    last_button = 0 
    if view_help:
        window.remove(main_view)
        window.append(help_view)
    else:
        window.remove(help_view)
        window.append(main_view)
        
def set_beats():
    global beats_per_measure
    beats = (1,2,3,4,6)
    index = beats.index(beats_per_measure) 
    index += 1 
    if index >= len(beats):
        index = 0
    beats_per_measure = beats[index]    
    beat_str = str(beats_per_measure)+'/4'
    if beats_per_measure == 6:
        beat_str = str(beats_per_measure)+'/8'
    lbl_beats.text = str(beat_str)

bpm = 100
display_bpm(bpm)

while True:
    delay = 60/bpm
    current_beat = 1
    get_buttons()
    if play:
        while current_beat <= beats_per_measure and play:
            if current_beat == 1 and accent:
                freq = 800
            else:
                freq = 500

            lbl_beat.text = str(current_beat)
            simpleio.tone(board.A0, freq, 0.01)
            delay_count = 0
            while delay_count < 10: # loop checking buttons between beats
                delay_count += 1
                get_buttons()
                time.sleep(delay/10)
            current_beat += 1
