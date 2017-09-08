from sys import platform

# TODO: Check port automatically
PORT = ''
if platform == 'darwin':
    PORT = '/dev/tty.usbmodem1411'
elif platform == 'linux':
    PORT = '/dev/ttyACM0'
else:
    PORT = 'com4'

BAUDRATE = 115200
