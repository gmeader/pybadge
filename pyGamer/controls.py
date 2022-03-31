# handle pyGamer buttons and joystick
import keypad
import board
import analogio

joystick_x = analogio.AnalogIn(board.JOYSTICK_X)
joystick_y = analogio.AnalogIn(board.JOYSTICK_Y)

last_joystick =''

# init keypad on PyGamer
k = keypad.ShiftRegisterKeys(
    clock=board.BUTTON_CLOCK,
    data=board.BUTTON_OUT,
    latch=board.BUTTON_LATCH,
    key_count=8,
    value_when_pressed=True,
)

# return a value from zero to 127
def getVoltage(pin):
    return int((pin.value / 65536) *127)
    return int((pin.value / 65536) *127)

# Return a direction if the joystick is changed
# Must push the joystick to an extreme position,
# as it is being used as a 4 way button pad
def check_joystick():
    global last_joystick
    x = getVoltage(joystick_x)
    y = getVoltage(joystick_y)
    if x < 10: value = 'left'
    elif x > 100: value = 'right'
    elif y < 10: value = 'up'
    elif y > 100: value = 'down'
    else:
        value = ''
    if value != last_joystick:
        last_joystick = value
        return value
    # joystick has not changed
    return ''

while True:
    joystick_value = check_joystick()
    if joystick_value:
        print(joystick_value)
    event = k.events.get() # check for button event
    if event:
        if event.pressed:
            print(event.key_number)
