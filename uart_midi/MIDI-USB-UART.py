# Simple USB Send MIDI
#beware of print statements, as they also send data to the UART!
import board
import time
import busio
import usb_midi

# init UART MIDI
# NB: We are just sending "raw" sysex MIDI data so I'm avoiding the MIDI library...
uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)

# Init USB MIDI
print(usb_midi.ports[1]) # make USB connect
time.sleep(2) # wait for USB to connect
port_in = usb_midi.ports[0]
port_out = usb_midi.ports[1]

def uart_send_message(msg):
    b = bytearray(msg)
    #print(b)
    #print('sending', len(b),'bytes to UART MIDI')
    uart.write(b)

def usb_send_message(msg):
    b = bytes(msg)
    sent = port_out.write(b)
    #print('sent',sent,'bytes to USB MIDI')


uart_send_message([0xB0,0x7B,0]) #all notes off

for i in range (6):
    time.sleep(.5)
    usb_send_message([0x90,0x3C-i,0x7F]) # NoteOn Channel 10 Middle C (note 60) Velocity: 127
    time.sleep(.5)
    msg = [0x90,0x3C-i,0x00] # NoteOn Channel 10 Middle C (note 60) Velocity: 0 (same as NoteOff)
    usb_send_message(msg)
    time.sleep(.1)
    uart_send_message([0x90,0x3C+i,0x7F]) # NoteOn Channel 1 Middle C (note 60) Velocity: 127
    time.sleep(.5)
    msg = [0x90,0x3C+i,0x00] # NoteOn Channel 1 Middle C (note 60) Velocity: 0 (same as NoteOff)
    uart_send_message(msg)

uart_send_message([0xB0,0x7B,0]) #all notes off
uart_send_message([0xFE]) # active sensing
