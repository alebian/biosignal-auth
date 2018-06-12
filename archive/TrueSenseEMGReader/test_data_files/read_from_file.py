import matplotlib.pyplot as plt

from true_sense import FilePacket, WirelessDataPacket


FILES = [
    'test_data_files/E20170908_174900_ALL.opi'
]


class Stream():
    def __init__(self, values=None):
        self._values = values or []
        self._current_idx = 0
        self._size = len(values)

    @classmethod
    def from_file(cls, file):
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


if __name__ == '__main__':
    for file in FILES:
        stream = Stream.from_file(file)
        packet = FilePacket.read_from_stream(stream, scale=True)

        wireless_data_frames = packet.payload

        adc_values = []
        temperatures = []
        accelerometers = []

        for data_frame in wireless_data_frames:
            if data_frame.has_data():
                temperatures.append(data_frame.temperature)
                accelerometers.append(data_frame.accelerometer)
                for x in data_frame.adc_values:
                    adc_values.append(x)

        plt.plot(adc_values)
        plt.show()
