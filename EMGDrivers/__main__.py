import settings

from true_sense import Controller

if __name__ == '__main__':
    ts = Controller(port=settings.PORT, baudrate=settings.BAUDRATE)
    ts.get_status()
