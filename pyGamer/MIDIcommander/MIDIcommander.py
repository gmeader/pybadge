# MIDI Commander for Adafruit PyGamer v1.0
# SysEx Patch Loader
#
# Deriviative work of the original SysEx “Librarian”
# from: @diyelectromusic
# https://diyelectromusic.wordpress.com/2022/05/28/raspberry-pi-pico-sysex-librarian/
#
#      MIT License
#
#      Copyright (c) 2022 diyelectromusic (Kevin)
#      more license details at end of code

## Modified for Adafruit PyGamer with MIDI Featherwing by Glenn Meader
## gmeader@gmail.com
# Files containing MIDI command bytes are to be stored on the SDcard in the /syx folder 
# and its subfolders. The UI enables navigation to subfolders.
# filenames and folder names may not start with a period
# Only files with a .syx extension are seen by this program
# You can put any MIDI command bytes into a file and this will send whatever is in the file,
# so you can send Program Change, CC and other - you are not limited to SYSEX commands
# Press the B button for Help

import board
import sdcardio
import storage
import os
import busio
import time
import errno
import re
import digitalio
import analogio # for joystick
import keypad
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

print(os.uname().machine)

display = board.DISPLAY
FONT = bitmap_font.load_font("fonts/helvB10.bdf")
TEXTHEIGHT = 10
#print('Display width:',display.width)
# FONT = terminalio.FONT

# Connect to the SDcard and mount the filesystem.
spi = board.SPI()
cs = board.SD_CS
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")
root_folder = "/sd/syx"

# MIDI init
# NB: We are just sending "raw" sysex MIDI data so I'm avoiding the MIDI library...
uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)

def send_message(msg):
    uart.write(bytearray(msg))

# Button Constants
BUTTON_A = 1
BUTTON_B = 0
BUTTON_START = 2
BUTTON_SEL = 3
# init keypad on PyGamer
k = keypad.ShiftRegisterKeys(
    clock=board.BUTTON_CLOCK,
    data=board.BUTTON_OUT,
    latch=board.BUTTON_LATCH,
    key_count=8,
    value_when_pressed=True,
)

# init joystick
joystick_x = analogio.AnalogIn(board.JOYSTICK_X)
joystick_y = analogio.AnalogIn(board.JOYSTICK_Y)
last_joystick =''
last_joystick_time = time.monotonic()

# return a value from zero to 127 for joystick values
def getVoltage(pin):
    return int((pin.value / 65536) *127)
    return int((pin.value / 65536) *127)

# Return a direction if the joystick is changed
# Must push the joystick to an extreme position,
# as it is being used as a 4 way button pad
def check_joystick():
    global last_joystick, last_joystick_time
    x = getVoltage(joystick_x)
    y = getVoltage(joystick_y)
    if x < 10:
        value = 'left'
    elif x > 100:
        value = 'right'
    elif y < 10:
        value = 'up'
    elif y > 100:
        value = 'down'
    else:
        value = ''

    # implement auto-repeat - holding the joystick for a while repeats the move
    if value == last_joystick: # is joystick still held
        # see if user held the joystick for more than 250ms
        elapsed = time.monotonic() - last_joystick_time
        if elapsed > 0.25:
            last_joystick_time = time.monotonic()
            return value

    # check to see if joystick has changed since last check
    if value != last_joystick:
        last_joystick_time = time.monotonic()
        last_joystick = value
        return value
    # otherwise joystick has not changed
    return ''

# see if we can access the root_folder
try:
    os.chdir(root_folder)
    print('Accessing SDcard',root_folder)
except OSError as exec:
    if exec.args[0] == errno.ENOENT:
        print ("ERROR: No "+root_folder+" directory found for files")

# get a list of files in the folder
def get_files(root_folder):
    files = os.listdir(root_folder) #list of files in folder
    fnregex = re.compile("\.syx$")
    file_names = []
    for f in files:
        # is it a directory
        stats = os.stat(root_folder + "/" + f)
        isdir = stats[0] & 0x4000
        #if it begins with a dot, skip it\
        if f[0] == '.':
            continue
        if isdir:
            file_names.append((f,'d')) # tag dirs with a 'd'
        else:
            # extract the file name and extension
            suffix = fnregex.search(f)
            if suffix:
                file_name = f[:suffix.start()]
                file_extension = f[suffix.start():suffix.end()]
                #print(file_name,file_extension)
                if file_extension == '.syx': # only collect .syX files
                    file_names.append((file_name,'f')) # tag files with a 'f'
    return file_names

# Set initial values
folder_path = root_folder
file_names = get_files(folder_path)
NUM_ITEMS = len(file_names)
print ("Number of items loaded:", NUM_ITEMS)
current_dirname = 'FOLDER'
selected_name_id = 0
selected_menu_row = 0
help = False

def sendSysExFromFile (fileidx):
    if fileidx >= len(file_names):
        return
    filename = folder_path+"/"+file_names[fileidx][0]+".syx"
    try:
        os.stat(filename)
    except OSError as exec:
        if exec.args[0] == errno.ENOENT:
            print ("ERROR: Cannot open filename: ", filename)
        else:
            print ("ERROR: Unknown error: ", exec.args[0])
        return

    print ("Reading: ", filename)
    with open (filename, "rb") as fh:
        sysex = fh.read()

    #print(sysex)
    written = uart.write(sysex)
    title.text = 'Sent: '+str(written)+' bytes'
    title.background_color=BACKCOLOUR
    title.color=0xFF00FF
    print ("Bytes sent: ", written)

#print ("Number of names = ", len(fnames))
#for n in range(len(fnames)):
#    print (n, "->", fnames[n])

menu_group = displayio.Group()

TITLECOLOUR = 0x000000
TITLEBKGCOLOR = 0xB0B0B0
TEXTCOLOUR = 0xFFFFFF
DIRCOLOUR = 0x00C000
BACKCOLOUR = 0x000000
HIGHCOLOUR = 0xFFFF00
HELPCOLOUR = 0x00FFFF

NUM_MENU_ROWS = 7
rows = []
# create array of Labels as rows on the screen (top row is Title)
title  = label.Label(FONT, text=" "*20,color=BACKCOLOUR, background_color=TITLEBKGCOLOR ,scale=1)
title.x = 0
title.y = 6
menu_group.append(title)

def set_title(str):
    strlen = len(str)
    pad_spaces = (20 - strlen)
    title.background_color=TITLEBKGCOLOR
    title.color=BACKCOLOUR
    title.text = " "*pad_spaces + str + " "*pad_spaces
    #print('LEN:',strlen,'WIDTH:',title.width, 'pad_spaces:',pad_spaces)
    #padding = (display.width - title.width) // 2
    #title.padding_left = padding
    #title.padding_right = padding
    #print('Padding:',padding)
    #print('Padding_left:',title.padding_left)
    #print('Padding_right:',title.padding_right)

for f in range(NUM_MENU_ROWS):
    namelab = label.Label(FONT, text=" "*10, color=TEXTCOLOUR, scale=1)
    namelab.x = 2
    namelab.y = 25+f*(TEXTHEIGHT+5)
    rows.append(namelab)
    menu_group.append(namelab)


def showMenu():
    global help
    help = False
    set_title(current_dirname)
    # figure out which item is the first displayed item based on selected_name_id
    # figure out which menu row is selected based on selected_name_id

    if NUM_ITEMS <= NUM_MENU_ROWS: # no scrolling because fewer items than rows
        selected_menu_row = selected_name_id
        start_item = 0
    else:
        # move highlight if within the first 4 items and menu is scrolled to top
        if selected_name_id < 3: # center row of menu
            selected_menu_row = selected_name_id # hilite the correct row
            start_item = 0
        # we are near the bottom of the items list (last 3 items on the list)
        elif selected_name_id >(NUM_ITEMS - NUM_MENU_ROWS+2):
            start_item = (NUM_ITEMS - NUM_MENU_ROWS) #scroll so the last item is in the last row
            selected_menu_row = selected_name_id - start_item # hilite teh correct row
        else:
            # we are at the center row of the menu
            selected_menu_row = 3
            start_item = selected_name_id - 3
            # scroll the list of menu items so that the selected on is in the center row

        # display all rows of the menu
    for r in range(NUM_MENU_ROWS):
        item_index = r + start_item
        if item_index < NUM_ITEMS:
            if file_names[item_index][1] == 'd':
                rows[r].text = str(item_index)+' /'+file_names[item_index][0]
                rows[r].color = DIRCOLOUR
            else:
                rows[r].text = str(item_index)+' '+file_names[item_index][0]
                rows[r].color = TEXTCOLOUR
        else:
            rows[r].text = " "*20
    rows[selected_menu_row].color = HIGHCOLOUR

def toggleHelp():
    global help, name_id
    if help:
        help=False
        # erase Help page
        updateMenuDisplay()
    else:
        help = True
        # display help page
        for d in range(NUM_MENU_ROWS):
            rows[d].color = HELPCOLOUR
        set_title('HELP')
        rows[0].text = 'B=Help toggle'
        rows[1].text = 'A=Enter Folder'
        rows[2].text = 'Up/Down=Scroll'
        rows[3].text = 'Right/Left=Page'
        rows[4].text = 'SEL=Send selected'
        rows[5].text = 'START=Top Menu'
        rows[6].text = ' '

def updateMenuDisplay():
    showMenu()
    display.show(menu_group)

def changeDir(dir_id):
    global file_names, folder_path, current_dirname, NUM_ITEMS, selected_name_id, selected_menu_row
    if dir_id == -1: # special flag to got to top folder
        folder_path = root_folder
        current_dirname = 'FOLDER'
    else:
        # is this a directory?
        if file_names[dir_id][1] == 'd':
            current_dirname = file_names[dir_id][0]
            folder_path = folder_path +'/'+ current_dirname
        else:
            return
    file_names = get_files(folder_path)
    NUM_ITEMS = len(file_names)
    print ('Folder:',current_dirname, '- items:',NUM_ITEMS)
    selected_name_id = 0
    selected_menu_row = 0
    updateMenuDisplay()

def itemDown ():
    # next item in list of menu items
    global selected_name_id
    selected_name_id += 1
    if selected_name_id >= NUM_ITEMS:
        selected_name_id = NUM_ITEMS-1 # stick at the bottom
    updateMenuDisplay()

def itemUp ():
    # prev item in list of menu items
    global selected_name_id
    selected_name_id -= 1
    if selected_name_id < 0:
        selected_name_id = 0 # stick at the top
    updateMenuDisplay()

def pageUp ():
    global selected_name_id
    selected_name_id -= NUM_MENU_ROWS
    if selected_name_id < 0:
        selected_name_id = 0
    updateMenuDisplay()

def pageDown ():
    global selected_name_id
    selected_name_id += NUM_MENU_ROWS
    if selected_name_id >= NUM_ITEMS:
        selected_name_id = NUM_ITEMS - 1
    updateMenuDisplay()

def pageBegin():
    changeDir(-1) # Home Folder

def sendFile ():
    sendSysExFromFile(selected_name_id)

updateMenuDisplay()

while True:
    joystick_value = check_joystick()
    if joystick_value == 'left':
        pageUp()
    elif joystick_value == 'right':
        pageDown()
    elif joystick_value == 'up':
        itemUp()
    elif joystick_value == 'down':
        itemDown()
    button_event = k.events.get() # check for button event
    if button_event:
        if button_event.pressed:
            #print(button_event.key_number)    # Reading buttons too fast returns 0
            if button_event.key_number == BUTTON_A :
                changeDir(selected_name_id)
            elif button_event.key_number == BUTTON_B:
                toggleHelp()
            elif button_event.key_number == BUTTON_SEL:
                sendFile()
            elif button_event.key_number == BUTTON_START:
                pageBegin()


#      Permission is hereby granted, free of charge, to any person obtaining a copy of
#      this software and associated documentation files (the "Software"), to deal in
#      the Software without restriction, including without limitation the rights to
#      use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#      the Software, and to permit persons to whom the Software is furnished to do so,
#      subject to the following conditions:
#
#      The above copyright notice and this permission notice shall be included in all
#      copies or substantial portions of the Software.
#
#      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#      IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#      FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#      COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHERIN
#      AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#      WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
