# check to see if PyBadge can write to its filesystem
# must have installed boot.py on the PyBadge
# and must hold a button while rebooting the PyBadge
import board
import digitalio
import storage
import time
try:
	with open("/test.txt", "a") as fp:
		fp.write("hello, world!")
        print('Wrote file')
except Exception as exc:
  error = exc
  print(error)
