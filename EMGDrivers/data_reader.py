from os import path

import logger
from true_sense import Packet


FILES = [
    'data/E20170908_174900_ALL.opi'
]


class Stream():
    def __init__(self, values):
        self._values = values
        self._current_idx = 0
        self._size = len(values)

    def from_file(file):
        ans = []
        with open(file, 'rb') as f:
            byte = f.read(1)
            while byte:
                ans.append(int.from_bytes(byte, byteorder='big'))
                byte = f.read(1)
        return Stream(ans)

    def read(self, amount):
        if amount <= 0:
            raise IndexError

        from_idx = self._current_idx
        to_idx = self._current_idx + amount
        ans = self._values[from_idx:to_idx]
        self._current_idx = to_idx
        return ans

    def has_next(self):
        return self._current_idx < self._size

    def __str__(self):
        return str.format('<Stream size={} idx={}>', self._size, self._current_idx)


# From OPIFileDefinition_v1.00_20130503.pdf
def interpret_file_bytes(stream):
    header = stream.read(512)[0:127]
    rest = []

    while stream.has_next():
        rest.append(Packet.read_from_stream(stream, logger.get_logger()))

    return (header, rest)


if __name__ == '__main__':
    for file in FILES:
        stream = Stream.from_file(file)
        header, packets = interpret_file_bytes(stream)

        for packet in packets:
            wired_frame = packet[1]
            print(wired_frame)
            print(str.format('Data code: {}', wired_frame[0]))
            break