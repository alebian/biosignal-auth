# sudo crontab -e
# @reboot python /home/pi/biosignal-auth/readerapp/status_reporter.py &
# mkdir /home/pi/logs
# */2 * * * * /home/pi/biosignal-auth/readerapp/status_reporter.py > /home/pi/logs/cronlog.log 2>&1
# To kill:
# ps aux | grep /home/pi/biosignal-auth/readerapp/status_reporter.py

import socket
import time
from mqtt.mqtt import Mqtt

def report():
    q = Mqtt()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    q.publish_state({'IP': s.getsockname()[0]})
    s.close()

if __name__ == "__main__":
    report()
