# CircuitPython for Adafruit PyBadge & PyGamer with MIDI featherwing
# by Glenn Meader (gmeader@gmail.com)
# display received DIN-5 MIDI clock messages as BPM
# display notes on a graphics matrix
# and  MIDI Messages on a text line: notes CC PC PB clock start,stop & continue commands
import board
import displayio
from adafruit_display_shapes.rect import Rect
import random
import time
import math
import terminalio
from adafruit_display_text import label
import busio

# can't use Adafruit MIDI library because it is too slow and drops notes and other received MIDI messages

# if you want to use USB MIDI instead of UART (DIN-5 connector) MIDI
# USB MIDI IN start receiving MIDI messages from USB, any MIDI channel
# midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel="ALL")

#  UART MIDI In and OUT:
# comment this out if you would rather use USB MIDI
uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)

# not used (yet)
def send_message(msg):
    uart.write(bytearray(msg))

fill_colors = [0xFF0000,0xFFD000,0xFFF000,0x00E000,0x00E0E0,0x0000E0,0xD000E0]

# format the text of MIDI messages
def format_cmd(cmd_name,note,velocity,channel):
    noteName = note_name(note)
    return "{0:2s} {1:3s} {2:3d} {3:3d} CH{4:2d}".format(cmd_name,noteName,note,velocity,channel+1)
    
# a complete MIDI message has been recieved
def handle_message(timestamp,msg):
    channel = msg[0] & 15
    cmd = (msg[0] & 240)
    #print (msg,channel,cmd)

    if cmd == 144: # NoteOn
        cmd_name = 'NO'
        note = msg[1]
        velocity = msg[2]
        noteName = note_name(note)
        y,x = note_position(note)
   
        if 0 <= y <= (max_y-1):
            if 0 <= x <= max_x:
                if velocity == 0:
                    matrix[x][y].fill = 0
                else:
                    matrix[x][y].fill = fill_colors[y]
        command_label.text = format_cmd(cmd_name,note,velocity,channel)

    elif cmd == 128: # NoteOff
        cmd_name = 'NF'
        note = msg[1]
        velocity = msg[2]
        note = msg[1]
        velocity = msg[2]
        noteName = note_name(note)
        y,x = note_position(note)
        if 0 <= y <= (max_y-1):
            if 0 <= x <= max_x:
                matrix[x][y].fill = 0
        command_label.text = format_cmd(cmd_name,note,velocity,channel)

    elif cmd == 160: #PolyAftertouch
        cmd_name = 'PA'
        note = msg[1]
        velocity = msg[2]
        noteName = note_name(note)
        command_label.text = format_cmd(cmd_name,note,velocity,channel)

    elif cmd == 176: #Control Change
        cmd_name = 'CC'
        control_number = msg[1]
        value = msg[2]
        command_label.text = "{0:2s} {1:3d} {2:3d}     CH{3:2d}".format(cmd_name,control_number,value,channel+1)

    elif cmd == 192: #Program Change
        cmd_name = 'PC'
        patch = msg[1]
        command_label.text = "{0:2s} {1:3d}       CH{2:2d}".format(cmd_name,patch,channel+1)
    
    elif cmd == 208: #Aftertouch
        cmd_name = 'AF'
        note = msg[1]
        velocity = msg[2]
        noteName = note_name(note)
        command_label.text = format_cmd(cmd_name,note,velocity,channel+1)

    elif cmd == 224: # PitchBend
        cmd_name = 'PB' 
        value = msg[2]*256+msg[1]
        command_label.text = "{0:2s} {1:5d}       CH{2:2d}".format(cmd_name,value,channel+1)
    
    elif cmd == 255: # SYSEX
        cmd_name = 'SYSEX'   
        command_label.text = cmd_name + ' CH '+str(channel+1)   
        
    if cmd > 144: # show previous command
        prev_label.text = command_label.text

first_c = 24 # MIDI note number of first octave C note

# calc the y,x location of the note in the matrix
def note_position(midi_note_number):
    n = midi_note_number - first_c
    return divmod(int(n),12)

note_names = 'C C#D D#E F F#G G#A A#B '
def note_name(midi_note_number):
    n = midi_note_number - first_c
    octave,note = divmod(int(n),12)
    first =note*2
    last = first+2
    noteName = note_names[first:last]
    return noteName.strip() + str(octave)

# setup display
screen = displayio.Group()
board.DISPLAY.show(screen)

prev_label = label.Label(terminalio.FONT, text="          ", color=0x808000,x=0,y=110)
command_label = label.Label(terminalio.FONT, text="          ", color=0xffff00,x=0,y=123)
clock_label = label.Label(terminalio.FONT, text="        ", color=0xE08000,x=124,y=123)
bpm_label = label.Label(terminalio.FONT, text="    BPM ", color=0x008000,x=118,y=110)
screen.append(prev_label)
screen.append(clock_label)
screen.append(command_label)
screen.append(bpm_label)

rect_size = 13
matrix = []
max_x = 12
max_y = 7

for y in range(max_y):
    for x in range(max_x):
        matrix.append([])
        matrix[x].append(y)
        matrix[x][y] = Rect(x*rect_size, y*rect_size, rect_size, rect_size, fill=0x0, outline=0x404040)
        screen.append(matrix[x][y])

# clear any notes form the matrix
def erase_matrix():
    for y in range(max_y):
        for x in range(max_x):
            matrix[x][y].fill = 0
    
ticks = 0
start = time.monotonic() # start the timer to measure clock ticks
ignore_data = True
bpm = 120

# Main loop
while True:
    raw_midi = uart.read(1)
    if raw_midi is not None:
        midi_byte = raw_midi[0]
        if midi_byte >= 248:
            # system realtime msgs
           
            if midi_byte == 248: # MIDI clock = 248
                ticks += 1
                if ticks == 24: # midi clock is 24 ticks per beat
                    beat_time = float(time.monotonic()-start)
                    bpm = math.floor(((60/beat_time) + bpm)/2) #average with last bpm value
                    # reset the timer, to start measuring the next beat
                    start = time.monotonic()
                    ticks = 0
                    bpm_label.text = "BPM {0:3d}".format(bpm)
                    #ignore_data = True
                continue
            '''
            if midi_byte == 242:
                # SPP = 242 + 2 bytes
                ignore_data = True # do not process data bytes until a valid status cmd arrives
                continue
                '''
            if midi_byte == 250:
                clock_label.text = "Start"
                erase_matrix()
            if midi_byte == 251:
                clock_label.text = "Continue"
            if midi_byte == 252:
                clock_label.text = "Stop"
            continue

        if midi_byte >= 240 : # system message 0xF0 and above
            ignore_data = True # do not process data bytes until a valid status cmd arrives
            continue

        is_status_msg = midi_byte >> 7

        if is_status_msg:
            # process MIDI command messages
            ignore_data= False
            channel = midi_byte & 15
            cmd = (midi_byte & 240)
            # reset the msg and build the correct size msg list for this cmd
            data_byte_counter = 0
            num_data_bytes = 2
            msg = [cmd+channel,0,0]
            if cmd in {12,13}:
                num_data_bytes = 1
                msg = [cmd,0]

        else:
            #  process MIDI data bytes
            if ignore_data == False:
                data_byte_counter += 1
                msg[data_byte_counter] = midi_byte
                if data_byte_counter >= num_data_bytes:
                    # message is complete
                    timestamp=time.monotonic()-start
                    handle_message(timestamp,msg)
                    # reset message list to current cmd status
                    msg=[cmd+channel,0] # make msg list the right size for the current cmd
                    if num_data_bytes == 2:
                        msg.append(0)
                    data_byte_counter=0


 
