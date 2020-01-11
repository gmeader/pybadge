import board
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect

title = label.Label(terminalio.FONT, text="Main Menu",color=0x0)
leftover = board.DISPLAY.width - title.bounding_box[2]
title.x =  int(leftover/2) #center
title.y = 5

dims = title.bounding_box
print(dims)

top = 40
left = 20
item_text = "Hello Glenn xyhgj"
text_area = label.Label(terminalio.FONT, text=item_text,color=0x0010f0)
text_area.x = left+5
text_area.y = top+5

item1_top = 86
item1_text = "Menu Item 1 y"
item1 = label.Label(terminalio.FONT, text=item1_text,color=0xffffff)
item1.x = 5
item1.y = item1_top + 5

item2_top =100
item2_text = "Menu Item 2g"
item2 = label.Label(terminalio.FONT, text=item2_text,color=0x0)
item2.x = 5
item2.y = item2_top + 5

# Make the display context
splash = displayio.Group(max_size=10)
board.DISPLAY.show(splash)

rect = Rect(80, 20, 41, 41, fill=0xFF0000,outline=0xFFFFFF)
splash.append(rect)

rect2 = Rect(left, top, text_area.bounding_box[2]+10, text_area.bounding_box[3], fill=0xFFFF00)
splash.append(rect2)
splash.append(text_area)

title_bkg = Rect(0, 0, board.DISPLAY.width, title.bounding_box[3], fill=0x888888)
splash.append(title_bkg)
splash.append(title)

item1_bkg = Rect(0, item1_top, board.DISPLAY.width, item1.bounding_box[3], fill=0x0, outline=0xFF0000)
splash.append(item1_bkg)
splash.append(item1)

item2_bkg = Rect(0, item2_top, board.DISPLAY.width, item2.bounding_box[3], fill=0xFFFFFF)
splash.append(item2_bkg)
splash.append(item2)

while True:
    pass