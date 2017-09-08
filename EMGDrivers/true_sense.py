from serial import Serial

SYNC_BYTE = 0x33

class Controller:
    def __init__(self, port, baudrate):
        self.serial = Serial(port=port, baudrate=baudrate, timeout=3)

    def get_status(self):
        packet = Packet.create_packet(0x10, [0x1])
        self.serial.write(packet)
        data = self._read_packet()
        print(list(data))

    def _read_packet(self):
        header = self.serial.read(4)
        if header[0] != SYNC_BYTE or header[1] != SYNC_BYTE:
            raise IOError
        payload_length = (header[2] << 8) + header[3]
        payload = list(self.serial.read(payload_length))
        checksum = self.serial.read(2)
        checksum = (checksum[0] << 8) + checksum[1]
        if sum(payload) != checksum:
            raise IOError
        return payload

class Packet:
    def create_packet(data_code, payload):
        wired = Packet._wired_packet(data_code, payload)
        return Packet._link_packet(wired)

    def _link_packet(payload):
        return [SYNC_BYTE, SYNC_BYTE] + Packet._get_length(payload) + payload + Packet._get_checksum(payload)

    def _wired_packet(data_code, payload):
        return [data_code] + payload

    def _get_checksum(payload):
        checksum = []
        chk = sum(payload)
        checksum.append(chk >> 8)
        checksum.append(chk)
        return checksum

    def _get_length(payload):
        packet_length = []
        packet_length.append(((len(payload)) >> 8) & 0xff)
        packet_length.append((len(payload)) & 0xff)
        return packet_length