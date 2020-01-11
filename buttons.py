import board
import digitalio
import time
from gamepadshift import GamePadShift

BUTTON_LEFT = const(128)
BUTTON_UP = const(64)
BUTTON_DOWN = const(32)
BUTTON_RIGHT = const(16)
BUTTON_SEL = const(8)
BUTTON_START = const(4)
BUTTON_A = const(2)
BUTTON_B = const(1)

speed = 1

pad = GamePadShift(digitalio.DigitalInOut(board.BUTTON_CLOCK),
                   digitalio.DigitalInOut(board.BUTTON_OUT),
                   digitalio.DigitalInOut(board.BUTTON_LATCH))

def check_buttons(buttons):
    if (buttons & BUTTON_RIGHT) > 0:
        print("Right")
    elif (buttons & BUTTON_LEFT) > 0:
        print("Left")
    elif (buttons & BUTTON_UP) > 0:
        print("Up")
    elif (buttons & BUTTON_DOWN) > 0:
        print("Down")
    elif (buttons & BUTTON_A) > 0:
        print("A")
    elif (buttons & BUTTON_B) > 0:
        print("B")
    elif (buttons & BUTTON_START) > 0:
        print("Start")
    elif (buttons & BUTTON_SEL) > 0:
        print("SELECT")

current_buttons = pad.get_pressed()
last_read = 0
while True:
    for color in range(0, 360, speed):
        if (last_read + 0.1) < time.monotonic():
            buttons = pad.get_pressed()
            last_read = time.monotonic()
        if current_buttons != buttons:
            check_buttons(buttons)
            current_buttons = buttons