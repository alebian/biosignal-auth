import matplotlib.pyplot as plt

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


def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)


def number_to_2s_complement(number, n):
    return number if (number >> n - 1) == 0 else number - (1 << n)


if __name__ == '__main__':
    for file in FILES:
        stream = Stream.from_file(file)
        header, packets = interpret_file_bytes(stream)

        values = []

        for packet in packets:
            packet_header = packet[0]
            wired_frame = packet[1] # payload

            data_code = wired_frame[0]
            sub_data_code = wired_frame[1]
            timestamp_values = wired_frame[2:8]
            timestamp = 0
            timestamp += timestamp_values[0] << (8 * 5)
            timestamp += timestamp_values[1] << (8 * 4)
            timestamp += timestamp_values[2] << (8 * 3)
            timestamp += timestamp_values[3] << (8 * 2)
            timestamp += timestamp_values[4] << (8 * 1)
            timestamp += timestamp_values[5]

            paired_device_number = wired_frame[8]
            miscellaneous_data = wired_frame[9]
            # 0 010 000 1
            adc_channel = wired_frame[10:-8]

            for high, low in grouped(adc_channel, 2):
                number = number_to_2s_complement((high << 6) + (low >> 2), 14)
                values.append((timestamp, number))

            temp_code = wired_frame[-8]
            temperature = temp_code * 1.13 - 46.8
            accelerometer = wired_frame[-7:-1]
            ed_measurement = wired_frame[-1]

        sorted_values = sorted(values, key=lambda pair: pair[0])
        adc_timestamps, adc_values = map(list, zip(*sorted_values))
        plt.plot(adc_values)
        plt.show()
