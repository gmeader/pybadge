# CircuitPython MIDI UART Thru test
# listens to MIDI on all channels and outputs whatever is received
# except all System Messages are ignored
# by gmeader on github
import board
import busio
import time

uart = busio.UART(board.TX, board.RX, baudrate=31250)

def send_message(msg):
    uart.write(bytearray(msg))
    
# a complete MIDI message has been recieved
def handle_message(msg):
    print(time.monotonic(),msg)
    send_message(msg)

print('MIDI Thru started')
msg =[]
ignore_data = False
while True:
    raw_midi = uart.read(1)
    midi_byte = raw_midi[0]
    if midi_byte >= 248:
        system_realtime_msg=[midi_byte]
        # uncomment if you need to send system realtime msgs
        # handle_message(system_realtime_msg) 
        continue
    if midi_byte >= 240 : # system message 0xF0 and above
        ignore_data = True # do not process data bytes until a valid status cmd arrives
        continue
        
    is_status = midi_byte >> 7

    if is_status:
        # process MIDI command messages
        ignore_data= False
        channel = midi_byte & 15
        cmd = (midi_byte & 240)
        # reset the msg and build the correct size msg list
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
                handle_message(msg)
                # reset message list to current cmd status
                msg=[cmd+channel,0] # make msg list the right size for the current cmd
                if num_data_bytes == 2:
                    msg.append(0)
                data_byte_counter=0
            
            
            
            
            
            




