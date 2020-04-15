import  mido
import time
import math

ports = mido.get_output_names()
print(ports)
port_name =''
# find the PyBadge port
for item in ports:
    if item[:7] == 'PyBadge':
        port_name = item
        break

if port_name != '':
    print('Opening port: '+port_name)
    port = mido.open_output(port_name)
    counter = 0
    start = True
    bpm = 60
    ppq = 24
    beat_ms = math.floor(60000/(bpm *ppq))
    beat_seconds = beat_ms / 1000
    print('BPM: '+str(bpm))
    print('beat_ms: ' + str(beat_ms))
    print('beat_seconds: ' + str(beat_seconds))
    while True:
        counter += 1
        msg = mido.Message('clock')
        port.send(msg)
        time.sleep(beat_seconds)

        if counter >= 100:
            counter = 0
            if start:
                msg = mido.Message('start')
                port.send(msg)
                start = False
            else:
                msg = mido.Message('stop')
                port.send(msg)
                start = True
else:
    print('No PyBadge port found\n')