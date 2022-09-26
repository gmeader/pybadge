# file read memory usage test

import board
import sdcardio
import storage
import gc
import os
import busio

# Connect to the SDcard and mount the filesystem.
spi = board.SPI()
cs = board.SD_CS
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")
root_folder = "/sd/syx"

uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)

start_mem = gc.mem_free()
print( "Available memory after init: {} bytes".format(start_mem) )

# see if we can access the root_folder
try:
    os.chdir(root_folder)
    print('Accessing SDcard',root_folder)
except OSError as exec:
    if exec.args[0] == errno.ENOENT:
        print ("ERROR: No "+root_folder+" directory found for files")

folderpath = root_folder+'/mrkhamer'
files = os.listdir(folderpath) #list of files in folder
print('Files in folder:',folderpath)
print(files)

def readfile(filepath):

    print (filepath)
    try:
        os.stat(filepath)
    except OSError as exec:
        if exec.args[0] == errno.ENOENT:
            print ("ERROR: Cannot open filename: ", filepath)
        else:
            print ("ERROR: Unknown error: ", exec.args[0])
        return


    print ("Reading: ", filepath)

    with open(filepath, "rb") as fh:
        midi_data = fh.read()

    written = uart.write(midi_data)
    print ("Bytes sent: ", written)
    del midi_data


  # test opening multiple files
def test_reading():

	for filename in files:
		filepath = folderpath +'/' + filename
		print(filepath)
		gc.collect()
		start_mem = gc.mem_free()
		print( "Before readfile Available memory: {} bytes".format(start_mem) )
		readfile(filepath)
		gc.collect()
		end_mem = gc.mem_free()
		print( "After readfile Available memory: {} bytes".format(end_mem) )
		print( "File read used {} bytes".format(start_mem - end_mem) )


test_reading()
