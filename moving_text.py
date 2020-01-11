import board
import terminalio
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import time

top = 10
bottom = 130
pos = top
text1 = "Hello world "
text2 = text1 + "    "
font = bitmap_font.load_font("fonts/Helvetica-Bold-16.bdf")
#font = terminalio.FONT

green = 0x00FF00
red = 0xFF0000
blue = 0x0000FF
yellow = 0xFFFF00
cyan = 0x00FFFF
magenta = 0xFF00FF
white = 0xFFFFFF

colors = [green,red,blue,yellow,cyan,magenta,white]

text_area = label.Label(font, text=text2, color=yellow)
text_area.x = 30
text_area.y = top
bkg = displayio.Group(max_size=10)
board.DISPLAY.show(bkg)
dims = text_area.bounding_box
print(dims)
rect = Rect(80, 20, 41, 41, fill=0x008000)
bkg.append(rect)

board.DISPLAY.show(text_area)
while True:
    pos = pos + 1
    text_area.y = pos
    text_area.color = colors[int(pos/20)]
    text_area.text = text1 + str(pos)
    time.sleep(0.01)
    if pos > bottom:
        pos = top
    pass