# File manager and Editor for MidiCommander
# by Glenn Meader 2022
# gmeader@gmail.com

# This program is an editing utility for use with MidiCommander.

# MidiCommander enables a user to "play" syx and .mic files stored in "playlists" on an SDcard, out to connected MIDI devices.
# It may be used to send MIDI data to several devices to configure a MIDI setup for each song during a gig.

# This program manages the files and playlist structure on the SDcard, and edits the contents of .mic files
# A .mic file simply contains one or more binary MIDI commands, typically Program Changes or CC, or any MIDI command
# a standard MIDI file (.mid) file is not used, as it is overly complex for this purpose, and no timing information is needed
# this program also manages .syx (files containing SYSEX data) but does not edit the contents of those.
import os,sys
import shutil
import PySimpleGUI as sg

folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'
ERROR_POPUP_BACKGROUND = '#800000'
POPUP_BACKGROUND = '#555570'

def find_syx_folder():
    # look at each drive on the machine for a root folder named 'syx'
    folder = [ chr(x) + ":/syx" for x in range(65,91) if os.path.exists(chr(x) + ":/syx") ]
    if len(folder):
        return folder[0]
    else:
        return sg.PopupGetFolder('/syx folder not found. Choose a folder to display')

STARTING_PATH = find_syx_folder()
if not os.path.exists(str(STARTING_PATH)):
    sg.PopupError("Can't find folder with MIDI data" )
    sys.exit(1)

treedata = sg.TreeData()
listbox_data = []
selected_type = ['dir']
selected_folder = STARTING_PATH
selected_path = STARTING_PATH

def reloadTree():
    global treedata
    global window
    treedata = sg.TreeData()
    addFilesInFolder('', STARTING_PATH)
    tree = window['_TREE_']
    tree.Widget.configure(show='tree')  # Hide header
    tree.update(values=treedata) # show_expanded=True,

def addFilesInFolder(parent, dirname):

    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname,f)
        if os.path.isdir(fullname):            # if it's a folder, add folder and recurse
            treedata.Insert(parent, fullname, f, values=['dir'], icon=folder_icon)
            addFilesInFolder(fullname, fullname)
        else:
            if f[0] != '.':
                treedata.Insert(parent, fullname, f, values=['file'], icon=file_icon)

def getFolders():
    folders = []
    for f in treedata.tree_dict:
        type = treedata.tree_dict[f].values
        if len(type):
            print(type[0])
            if type[0] == 'dir':
                folders.append(f)
    return folders

note_names = 'C C#D D#E F F#G G#A A#B '
first_c = 24  # MIDI note number of first octave C note

def noteName(midi_note_number):
    n = midi_note_number - first_c
    octave, note = divmod(int(n), 12)
    first = note * 2
    last = first + 2
    the_note_name = note_names[first:last]
    return the_note_name.strip() + str(octave)

CC_names=[
    'Bank Select MSB',
    'Mod Wheel MSB',
    'Breath MSB',
    'Undefined 3',
    'Foot Pedal MSB',
    'Portamento Time MSB',
    'Data Entry MSB',
    'Volume',
    'Balance MSB',
    'Undefined 9',
    'Pan MSB',
    'Expression',
    'Effect 1',
    'Effect 2',
    'Undefined 14',
    'Undefined 15',
    'General Purpose 1',
    'General Purpose 2',
    'General Purpose 3',
    'General Purpose 4',
    'Undefined 20',
    'Undefined 21',
    'Undefined 22',
    'Undefined 23',
    'Undefined 24',
    'Undefined 25',
    'Undefined 26',
    'Undefined 27',
    'Undefined 28',
    'Undefined 29',
    'Undefined 30',
    'Undefined 31',
    'LSB 0',
    'LSB 1',
    'LSB 2',
    'LSB 3',
    'LSB 4',
    'LSB 5',
    'LSB 6',
    'LSB 7',
    'LSB 8',
    'LSB 9',
    'LSB 10',
    'LSB 11',
    'LSB 12',
    'LSB 13',
    'LSB 14',
    'LSB 15',
    'LSB 16',
    'LSB 17',
    'LSB 18',
    'LSB 19',
    'LSB 20',
    'LSB 21',
    'LSB 22',
    'LSB 23',
    'LSB 24',
    'LSB 25',
    'LSB 26',
    'LSB 27',
    'LSB 28',
    'LSB 29',
    'LSB 30',
    'LSB 31',
    'Damper Pedal',
    'Portamento',
    'Sustenuto Pedal',
    'Soft Pedal',
    'Legato',
    'Hold 2',
    'Sound Controller 1',
    'Sound Controller 2 Resonance',
    'Sound Controller 3 Release Time',
    'Sound Controller 4 Attack',
    'Sound Controller 5 Cutoff',
    'Sound Controller 6',
    'Sound Controller 7',
    'Sound Controller 8',
    'Sound Controller 9',
    'Sound Controller 10',
    'General Purpose 5 Decay',
    'General Purpose 6 Hi Pass Filter',
    'General Purpose 7',
    'General Purpose 8',
    'Portamento amount',
    'undefined 85',
    'undefined 86',
    'undefined 87',
    'Hi Rez Velocity Prefix',
    'undefined 89',
    'undefined 90',
    'Effect 1 Depth Reverb',
    'Effect 2 Depth Tremelo',
    'Effect 3 Depth Chorus',
    'Effect 4 Depth Detune',
    'Effect 5 Depth Phaser',
    'Data Increment',
    'Data Decrement',
    'NRPN LSB',
    'NRPN MBB',
    'RPN LSB',
    'RPN MSB',
    'undefined 102',
    'undefined 103',
    'undefined 104',
    'undefined 105',
    'undefined 106',
    'undefined 107',
    'undefined 108',
    'undefined 109',
    'undefined 110',
    'undefined 111',
    'undefined 112',
    'undefined 113',
    'undefined 114',
    'undefined 115',
    'undefined 116',
    'undefined 117',
    'undefined 118',
    'undefined 119',
    'All Sound Off',
    'Reset Controllers',
    'Local Control',
    'All Notes Off',
    'Omni Mode Off',
    'Omni Mode On',
    'Mono Mode',
    'Poly Mode'
]

# read the contents of a .mic file into a list
def parseMidiFile(path):
    result=[]
    with open(path, mode='rb') as file:
        fileContent = file.read()
        #print('File bytes:',len(fileContent))
        cmd_list = parseMidiData(fileContent)
        print ('MIDI commands read:', len(cmd_list))
        #print(cmd_list)
        return cmd_list # returns a list of midi commands

# parse the data from a data string into a list of MIDI commands
def parseMidiData(data):
    # detects MIDI commands in a byte stream and packages them into lists with cmd and data
    commands = [] # return a list of parsed commands
    for midi_byte in data:
        #print('midi_byte',midi_byte)
        if midi_byte >= 248:
            # system realtime msgs

            if midi_byte == 248:  # F8h MIDI clock
                commands.append('Clock')
                continue
            if midi_byte == 242: # F2h SPP
                ignore_data = True # do not process data bytes until a valid status cmd arrives
                commands.append('SPP')
                continue
            if midi_byte == 250: # FAh
                cmd = "Start"
                commands.append(cmd)
            if midi_byte == 251: # FBh
                cmd = "Continue"
                commands.append(cmd)
            if midi_byte == 252: # FCh
                cmd = "Stop"
                commands.append(cmd)
            continue

        if midi_byte >= 240:  # system message 0xF0 and above
            ignore_data = True  # do not process data bytes until a valid status cmd arrives
            continue

        is_status_msg = midi_byte >> 7 # check the MSB to see if it is a status msg

        if is_status_msg:
            # process MIDI command messages
            ignore_data = False
            channel = midi_byte & 15
            cmd = (midi_byte & 240) # strip out channel number

            # reset the msg and build the correct size msg list for this cmd
            data_byte_counter = 0
            num_data_bytes = 2
            msg = [cmd + channel, 0, 0]
            if cmd in {208, 192}: # D0h Channel Pressure, C0h Program Change
                num_data_bytes = 1
                msg = [cmd + channel, 0]

        else:
            #  process MIDI data bytes
            if ignore_data == False:
                data_byte_counter += 1
                msg[data_byte_counter] = midi_byte
                if data_byte_counter >= num_data_bytes:
                    # message is complete
                    #print (msg)
                    commands.append(parseMidiMessage( msg))
                    # reset message list to current cmd status
                    msg = [cmd + channel, 0]  # make msg list the right size for the current cmd
                    if num_data_bytes == 2:
                        msg.append(0)
                    data_byte_counter = 0
    return commands

# take the bytes of a MIDI message (typically 3 or 4 bytes) and return a tuple with the decoded message
def parseMidiMessage(msg):
    result = ''
    channel = msg[0] & 15
    cmd = (msg[0] & 240)

    if cmd == 144: # 90h NoteOn
        note = msg[1]
        note_name = noteName(note)
        velocity = msg[2]
        cmd_title = 'NoteOn:' + str(note)+' '+note_name +' '+str(velocity) + ' CH:'+str(channel+1)
        #print(' ',cmd_name, note, noteName, velocity,channel)
        return (cmd_title, cmd, note, velocity, channel)

    elif cmd == 128: # 80h NoteOff
        note = msg[1]
        velocity = msg[2]
        note_name = noteName(note)
        cmd_title = 'NoteOff:' + str(note) + ' ' + note_name + ' ' + str(velocity)+ ' CH:'+str(channel+1)
        #print(' ',cmd_name, note, noteName, velocity,channel)
        return (cmd_title, cmd, note, velocity, channel)

    elif cmd == 160:  # A0h PolyAftertouch
        note = msg[1]
        velocity = msg[2]
        note_name = noteName(note)
        cmd_title = 'Poly Aftertouch:' + str(note) + ' ' + note_name + ' ' + str(velocity)+ ' CH:'+str(channel+1)
        #print(' ',cmd_name, note, noteName,velocity,channel)
        return (cmd_title, cmd, note, velocity, channel)

    elif cmd == 176:  # B0h Control Change
        control_number = msg[1]
        value = msg[2]
        cmd_title = 'CC' + str(control_number)+': '+ CC_names[control_number] + ': '+str(value)+ ' CH:'+str(channel+1)
        #print(' ',cmd_name, control_number, value,'CH',channel)
        return (cmd_title, cmd, control_number, value, channel)

    elif cmd == 192:  # C0h Program Change
        patch = msg[1] # only one databyte
        cmd_title = 'ProgramChange:'+str(patch) + ' CH:'+str(channel+1)
        #print(' ',cmd_name, patch, 'CH',channel)
        return (cmd_title, cmd, patch, channel)

    elif cmd == 208:  # D0h Aftertouch - Channel Pressure
        velocity = msg[1] # only one databyte
        cmd_title = 'Channel Pressure:' + str(velocity) + ' CH:'+str(channel+1)
        #print(' ',cmd_name, velocity, 'CH',channel)
        return (cmd_title, cmd, velocity, channel)

    elif cmd == 224:  # E0h PitchBend
        value = msg[2] * 256 + msg[1]
        cmd_title = 'Pitchbend:'+str(value) + ' CH:'+str(channel+1)
        #print(' ',cmd_name, value, 'CH',channel)
        return (cmd_title, cmd,  msg[1], msg[2], channel)

    elif cmd == 255:  # FFh SYSEX
        cmd_title = 'SYSEX'
        # not processing the SYSEX data
        #print(' ',cmd_name + ' CH ',channel)
        return (cmd_title, cmd, channel)

# read disk directory into treedata
addFilesInFolder('', STARTING_PATH)

# main window layout
layout = [[ sg.Text(STARTING_PATH,key='_Title_') ],
           [sg.Frame('File & Folder',
                [[sg.Button('New Folder',key='_NewFolder_')],
                [sg.Button('New File',key='_NewFile_')],
                [sg.Button('Rename',key='_RenameFile_')],
                [sg.Button('Move',key='_MoveFile_')],
                [sg.Button('Copy',key='_CopyFile_')],
                [sg.Button('Delete',key='_DeleteFile_')]],
                element_justification='c',
                tooltip='Select a file or folder, then click button'),

            sg.Tree(data=treedata, headings=[],auto_size_columns=True, num_rows=20, col0_width=30, key='_TREE_', enable_events=True, show_expanded=False,),
            sg.Listbox(
                        key='_LIST_',
                        values=listbox_data,
                        size=(54, 20),
                        enable_events=True),
            sg.Frame('Row',
                [[sg.Button('Edit',key='_EditRow_')],
                [sg.Button('New',key='_NewRow_')],
                [sg.Button('Move',key='_MoveRow_')],
                [sg.Button('Copy',key='_CopyRow_')],
                [sg.Button('Delete',key='_DeleteRow_')]],
                element_justification='c',
                tooltip='Select a row, then click button')
            ],
          [ sg.Button('Quit'),
            sg.Text('                                                                                                                              '),
            sg.Button('Save File')]]

window = sg.Window('Editor for MidiCommander SDcard files').Layout(layout)

# popup window to edit a MIDI command
def edit_window(title,cmd,original):
    cmd_index = (cmd >> 4) - 8 # convert cmd value (such as 80h for NoteOn to list index)
    command_list = ['NoteOff','NoteOn','Aftertouch Poly','CC Control Change','Program Change','Channel Pressure','Pitch Bend']
    default_command = command_list[cmd_index]
    editor_layout = [
        [sg.Text(title)],
        [sg.Text("MIDI Command:"),sg.Combo(command_list,default_value=default_command)],
        [sg.Text("Note/Number:"),sg.InputText(key='data1', size=(5, 1)),sg.Text(" ",text_color='#800000',key='-errormsg-')],
        [sg.Text("Velocity/Value:"),sg.InputText(key='data2', size=(3, 1))],
        [sg.Text("Channel:"),sg.Combo([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],key='channel')],
        [sg.Button("Save"), sg.Button("Close")]
        ]

    modal_window = sg.Window("Edit", editor_layout, size=(400, 250),finalize=True, modal=True, keep_on_top=True)
    sg.fill_form_with_values(window=modal_window, values_dict=original)
    result = False
    while True:
        event, values = modal_window.read()
        if event in ("Close", sg.WIN_CLOSED):
            break
        # save command into the listbox
        elif event == "Save":
            #format the values into a tuple (title, cmd, value, velocity, channel)
            #print('NEW VALUES:',values)
            title = values[0]
            cmd = command_list.index(values[0])
            channel = values['channel']
            if cmd == 0:
                title = 'NoteOFF: ' + str(values['data1']) + ' V:' + str(values['data2']) + ' CH:' + str(channel)
            elif cmd == 1:
                title = 'NoteON: ' + str(values['data1']) + ' V:' + str(values['data2']) + ' CH:' + str(channel)
            elif cmd == 2:
                title = 'Aftertouch: ' + str(values['data1']) + ' V:' + str(values['data2']) + ' CH:' + str(channel)
            elif cmd == 3: # format title for CC command
                title = 'CC'+str(values['data1'])+': '+CC_names[int(values['data1'])]
            elif cmd == 4: # format title for PC command
                title = 'Program Change: ' + str(values['data1']) + ' CH:'+str(channel)
                values['data2'] = 0
            elif cmd == 5:
                title = 'Channel pressure: ' + str(values['data2']) + ' CH:'+str(channel)
                values['data1'] = 0
            elif cmd == 6:
                value = int(values['data2']) * 256 + int(values['data1'])
                title = 'Pitchbend:' + str(value) + ' CH:'+str(channel)

            # check to make sure data1 and data2 are in the range 0-127
            if int(values['data1']) > 127 or int(values['data2']) > 127 or int(values['data1']) < 0 or int(
                    values['data2']) < 0:
                modal_window['-errormsg-'].update('must be between 0 and 127')
                continue
            midi_cmd = (cmd+8) << 4
            result = (title, midi_cmd, int(values['data1']), int(values['data2']), int(channel))
            print('EDIT WINDOW RESULT:', result)
            break

    modal_window.close()
    return result

def isDirSelected():
    if len(selected_type) == 1 and selected_type[0] == 'dir':
        return True
    else:
        return False

def isFileSelected():
    if len(selected_type) == 1 and selected_type[0] == 'file':
        return True
    else:
        return False

def isMidiFileSelected():
    if len(selected_type) == 1 and selected_type[0] == 'file':
        file_name = os.path.basename(selected_path)
        (name, extension) = os.path.splitext(file_name)
        if extension == '.mic':
            return True
    return False

# Main Event Loop
while True:
    event, values = window.Read()
    #print(event,values)
    if event in (None, 'Quit'):
        break

    if event =='_TREE_': # user clicks in tree
        if len(window.Element('_TREE_').SelectedRows):
            selected_row = window.Element('_TREE_').SelectedRows[0]
            selected_type = window.Element('_TREE_').TreeData.tree_dict[selected_row].values
            selected_path = values['_TREE_'][0]
        else:
            # User selected a folder, make it the currently selected folder
            selected_row = None
            selected_type = ['dir']
            selected_folder = STARTING_PATH
            selected_path = STARTING_PATH

        if len(selected_type) == 1 and selected_type[0] == 'file':
            # user clicked on a filename
            if isFileSelected():
                # if it is a MIDI file, not a SYSEX file, we can load its contents
                if isMidiFileSelected():
                    # read and parse the file
                    listbox_data = parseMidiFile(selected_path)
                    # print('LISTBOX_DATA:', listbox_data)
                else:
                    print('Cannot edit SYX files')
                    listbox_data = []
                window["_LIST_"].update(listbox_data)

### FILE SYSTEM TREE BUTTON EVENTS

    # create a new folder in the currently selected folder
    if event == '_NewFolder_':
        # Check to see if we are pointed at a folder to create the folder in
        if not isDirSelected():
            selected_path = STARTING_PATH # select root folder
        parent_folder = os.path.basename(selected_path)
        new_folder_name = sg.popup_get_text("Name for new folder in "+parent_folder,no_titlebar=True,background_color=POPUP_BACKGROUND)
        new_path = selected_path+'/'+new_folder_name

        if not os.path.isdir(new_path):
            # create the folder
            try:
                print('Create Folder', new_path)
                os.mkdir(new_path)
                reloadTree()
            except OSError as error:
                print(error)
        else:
            sg.popup("You must select a folder to contain the new folder first",no_titlebar=True,background_color=ERROR_POPUP_BACKGROUND)

    # create a new file in the currently selected folder
    if event == '_NewFile_':
        # Check to see if we are pointed at a folder to create the new file in
        if isDirSelected():
            parent_folder = os.path.basename(selected_path)
            new_file_name = sg.popup_get_text("Name for new file in "+parent_folder, no_titlebar=True, background_color=POPUP_BACKGROUND)
            (name,extension) = os.path.splitext(new_file_name)
            if extension != '.mic':
                new_file_name += '.mic'
            new_pathname=selected_path + '/' + new_file_name
            print('Create file', new_pathname)
            if not os.path.isfile(new_pathname):
                # create the empty file
                f = open(new_pathname, 'w')
                f.close()
                # reload tree
                reloadTree()
        else:
            sg.popup("You must select a folder to contain the new file first", no_titlebar=True,background_color=ERROR_POPUP_BACKGROUND)

    # rename a file or folder
    if event == '_RenameFile_':
        # Check to see if we are pointed at a folder or file
        if isFileSelected():
            old_file_name = os.path.basename(selected_path)
            (old_name, old_extension) = os.path.splitext(old_file_name)
            new_file_name = sg.popup_get_text("New name for:" + selected_path, no_titlebar=True, background_color=POPUP_BACKGROUND)
            (name, extension) = os.path.splitext(new_file_name)
            print(name, 'extension:', extension)
            if extension == '':
                new_file_name += old_extension
            new_pathname = os.path.dirname(selected_path) + '/' + new_file_name
        elif isDirSelected():
            old_dir_name = os.path.basename(selected_path)
            new_dir_name = sg.popup_get_text("New name for:" + selected_path, no_titlebar=True, background_color=POPUP_BACKGROUND)
            new_pathname = os.path.dirname(selected_path) + '/' + new_dir_name
        else:
            sg.popup("You must select a file or folder to rename first", no_titlebar=True, background_color=ERROR_POPUP_BACKGROUND)
            continue

        # does new filename already exist?
        if not os.path.exists(new_pathname):
            print('Rename:', selected_path, new_pathname)
            os.rename(selected_path,new_pathname)
            reloadTree()
        else:
            sg.popup( new_pathname + ' already exists.', no_titlebar=True,background_color=ERROR_POPUP_BACKGROUND)

    # move the selected file to another folder
    if event == '_MoveFile_':
        folders = getFolders()
        if isFileSelected():
            file_name = os.path.basename(selected_path)
            # popup a combo box that lists the folders
            destination_folder_path = sg.popup_get_folder("Destination folder for :"+file_name,initial_folder=STARTING_PATH,no_titlebar=True, background_color=POPUP_BACKGROUND)
            # does destination folder exist?
            if destination_folder_path != None and os.path.isdir(destination_folder_path):
                print('Move file', selected_path, destination_folder_path)
                shutil.move(selected_path, destination_folder_path)
                reloadTree()
            else:
                sg.popup("You must provide an existing destination folder", no_titlebar=True,
                         background_color=ERROR_POPUP_BACKGROUND)
        else:
            sg.popup("You must select a file to rename first", no_titlebar=True, background_color=ERROR_POPUP_BACKGROUND)

    # copy the selected file to another folder
    if event == '_CopyFile_':
        if isFileSelected():
            file_name = os.path.basename(selected_path)
            destination_folder_path = sg.popup_get_folder("Destination folder for: " + file_name,
                                                          initial_folder=STARTING_PATH,
                                                          no_titlebar=True,
                                                          background_color=POPUP_BACKGROUND)
            # does destination folder exist?
            if destination_folder_path != None and os.path.isdir(destination_folder_path):
                destination_path = destination_folder_path + '/' + file_name
                print('Copy file', selected_path, destination_path)
                shutil.copy(selected_path, destination_path)
                reloadTree()
            else:
                sg.popup("You must select a destination for the copy", no_titlebar=True,
                         background_color=ERROR_POPUP_BACKGROUND)
        else:
            sg.popup("You must select a file to copy first", no_titlebar=True,background_color=ERROR_POPUP_BACKGROUND)

    if event == '_DeleteFile_':
        if isFileSelected():
            file_name = os.path.basename(selected_path)
            if sg.popup_yes_no("Delete:" + file_name, no_titlebar=True, background_color=POPUP_BACKGROUND):
                if os.path.isfile(selected_path):
                    try:
                        print('Delete file', selected_path)
                        os.remove(selected_path)
                        reloadTree()
                    except OSError as error:
                        print(error)

        elif isDirSelected():
            folder_name = os.path.basename(selected_path)
            if sg.popup_yes_no("Delete:" + folder_name, no_titlebar=True, background_color=POPUP_BACKGROUND):
                if os.path.isdir(selected_path):
                    try:
                        print('Delete folder', selected_path)
                        os.remove(selected_path)
                        reloadTree()
                    except OSError as error:
                        print(error)
        else:
            sg.popup("You must select a file to copy first", no_titlebar=True,background_color=ERROR_POPUP_BACKGROUND)

###########################
#   FILE EDITOR LISTBOX BUTTON EVENTS

    if event == '_NewRow_':
        # is a file selected?
        if not isMidiFileSelected():
            sg.popup("You must first select a .mic file.", no_titlebar=True, background_color=ERROR_POPUP_BACKGROUND)
            continue

        title = 'CC'
        cmd = 176  # B0 as a default command
        row_data = {
            'data1': 0,
            'data2': 0,
            'channel': 1
        }
        results = edit_window('new',cmd,row_data)
        # append row to list
        if results:
            listbox_data.append(results)
            window.Element('_LIST_').update(listbox_data)

    if event == '_MoveRow_':
        indexes = window.Element('_LIST_').get_indexes()
        if not indexes:
            sg.popup_ok('You must select a row to move', no_titlebar=True, background_color=ERROR_POPUP_BACKGROUND)
            continue
        location = sg.popup_get_text('Move Row '+str(indexes[0]+1)+' to row number:',no_titlebar=True, background_color=POPUP_BACKGROUND)  # Provide a Combo of names/ rows where to place
        if location.isnumeric():
            # if the number is in the range of 0 to len(listbox_data)
            location = int(location) - 1
            if location in range(0, len(listbox_data)):
                element = listbox_data[indexes[0]]
                listbox_data.pop(int(indexes[0]))
                if location > len(listbox_data):
                    listbox_data.append(element)
                else:
                    listbox_data.insert(int(location), element)
                window.Element('_LIST_').update(listbox_data)
    if event == '_CopyRow_':
        indexes = window.Element('_LIST_').get_indexes()
        if not indexes:
            sg.popup_ok('You must select a row to copy', no_titlebar=True, background_color=ERROR_POPUP_BACKGROUND)
            continue
        answer = sg.popup_yes_no('Copy Row '+str(indexes[0]+1),no_titlebar=True, background_color=POPUP_BACKGROUND)  # Provide a Combo of names/ rows where to place
        if answer == 'Yes':
            element = listbox_data[indexes[0]]
            listbox_data.append(element)
            window.Element('_LIST_').update(listbox_data)

    if event == '_DeleteRow_':
        indexes = window.Element('_LIST_').get_indexes()
        if not indexes:
            sg.popup_ok('You must select a row to delete',no_titlebar=True, background_color=ERROR_POPUP_BACKGROUND)
            continue
        answer = sg.popup_yes_no('Delete Row '+str(indexes[0]+1),no_titlebar=True, background_color=POPUP_BACKGROUND)
        if answer == 'Yes':
            listbox_data.pop(int(indexes[0]))
            window.Element('_LIST_').update(listbox_data)

    if event == '_EditRow_':
        indexes = window.Element('_LIST_').get_indexes()
        if not indexes:
            sg.popup_ok('You must select a row to edit',no_titlebar=True, background_color=ERROR_POPUP_BACKGROUND)
            continue
        row_index = indexes[0]
        title = values['_LIST_'][0][0]
        cmd = values['_LIST_'][0][1]
        data1 = values['_LIST_'][0][2]
        if cmd in (192, 208): # one byte commands
            channel = values['_LIST_'][0][3]
        else:
            data2 = values['_LIST_'][0][3]
            channel = values['_LIST_'][0][4]
        cmd_index = cmd >> 4

        # construct the right number of items for the row_data, based on the type of command
        if cmd in[192]: # ProgramChange, ChannelPressure
            row_data = {
                'data1': data1,
                'data2': None,
                'channel': channel + 1  # add one to make it user friendly
            }
        elif cmd == 208:
            row_data = {
                'data1': None,
                'data2': data1,
                'channel': channel + 1  # add one to make it user friendly
            }
        else:
            row_data={
                'data1': data1,
                'data2': data2,
                'channel':channel + 1 # add one to make it user friendly
                }
        # display row editor window for row(index)
        results = edit_window(title,cmd,row_data)
        # remember to subtract one from channel
        # results is a tuple with channel as the 5th element
        # store edited values in the listbox
        if results:
            listbox_data[row_index] = results
            window["_LIST_"].update(listbox_data)

    if event == 'Save File':
        if not isMidiFileSelected():
            sg.popup("You must first select a .mic file to save.", no_titlebar=True, background_color=ERROR_POPUP_BACKGROUND)
            continue
        if len(listbox_data) == 0:
            sg.popup("Nothing to save.", no_titlebar=True,background_color=ERROR_POPUP_BACKGROUND)
            continue
        print('Number of commands:', len(listbox_data))
        # open file for write
        with open(selected_path, mode='wb') as file:
            # write all the MIDI commands
            #print('SAVE:',listbox_data)
            for command in listbox_data:
                #print (command)
                title, cmd, data1, data2, channel = command
                status_byte = cmd + (channel - 1)
                if cmd in [192,208]: # only 2 bytes in the command
                    cmd_list = [status_byte, data1]
                else:
                    cmd_list = [status_byte, data1, data2]
                thebytes = bytes(cmd_list)
                file.write(thebytes)


