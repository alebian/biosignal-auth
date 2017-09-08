from serial import Serial

import settings

SYNCBYTE = 0x33


class TrueSense:
    def __init__(self):
        self.serial = Serial(port=settings.PORT, baudrate=settings.BAUDRATE, timeout=3)


    def get_status(self):
        packet = Packet.create_packet(0x10, [0x1])
        #packet = [0x33, 0x33, 0, 2, 0x10, 0x1, 0, 0x11]
        self.serial.write(packet)
        print(packet)
        data = self.serial.read(1)
        print(list(data))



class Packet:
    def _link_packet(payload):
        return [SYNCBYTE, SYNCBYTE] + Packet._get_length(payload) + payload + Packet._get_checksum(payload)

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

    def create_packet(data_code, payload):
        wired = Packet._wired_packet(data_code, payload)
        return Packet._link_packet(wired)

if __name__ == '__main__':
    ts = TrueSense()
    ts.get_status()