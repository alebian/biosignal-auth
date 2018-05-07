from serial import Serial, SerialException, EIGHTBITS, PARITY_NONE, STOPBITS_ONE

from logger import get_logger
import settings

class Controller(object):
    def __init__(self, scale=True):
        self.scale = scale
        self._logger = get_logger()
        self.serial = False
        # Try all known ports
        for port in settings.POSSIBLE_PORTS:
            try:
                self.serial = Serial(port=port, baudrate=settings.BAUDRATE, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=3)
                self._logger.info(str.format("Using device in port: {}", port))
                break
            except SerialException:
                continue
        if not self.serial:
            self._logger.error('Device not found in any of the known ports')
            raise SerialException

    def read_data(self, times):
        i = 0
        while i < times:
            packet = self._read_packet()
            yield packet
            i+=1

    def _read_packet(self):
        self._logger.info("reading packet")
        sync2 = 0
        while sync2 != 90:
            sync1 = int.from_bytes(self.serial.read(), 'big')
            while sync1 != 165:
                sync1 = int.from_bytes(self.serial.read(), 'big')
                self._logger.debug("sync1: %d", sync1)

            sync2 = int.from_bytes(self.serial.read(), 'big')
            self._logger.debug("sync2: %d", sync2)

        version = int.from_bytes(self.serial.read(), 'big')
        count = int.from_bytes(self.serial.read(), 'big')
        channels = []
        for _ in range(0,6):
            channels.append(int.from_bytes(self.serial.read(2),byteorder='big'))
        state = int.from_bytes(self.serial.read(), byteorder='big')

        return DataPacket(version, count, channels, state)

    def close(self):
        self.serial.close()

    def __del__(self):
        if self.serial:
            self.close()

class DataPacket(object):
    def __init__(self, version, count, channels, state):
        self.version=version
        self.count=count
        self.channels=channels
        self.state=state
        
        