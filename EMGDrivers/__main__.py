import time
import matplotlib.pyplot as plt
import numpy as np

from true_sense import Controller
import logger
from true_sense import Packet


def interpret_file_bytes(stream):
    rest = []

    while stream.has_next():
        rest.append(Packet.read_from_stream(stream, logger.get_logger()))

    return rest


def basic(code, sub_code, msg):
    # print(msg)
    header, payload, checksum = ts.basic_request(code, sub_code)
    # print(header)
    # print(payload)
    return (header, payload, checksum)


def grouped(iterable, n):
    return zip(*[iter(iterable)] * n)


def number_to_2s_complement(number, n):
    return number if (number >> n - 1) == 0 else number - (1 << n)


def analyze_data_payload(wired_frame):
    if wired_frame[0] == 64:
        return wired_frame

    values = []
    print(wired_frame)
    data_code = wired_frame[0]
    sub_data_code = wired_frame[1]
    timestamp_values = wired_frame[2:8]

    paired_device_number = wired_frame[8]
    miscellaneous_data = wired_frame[9]
    # 0 010 000 1
    adc_channel = wired_frame[10:-8]

    for high, low in grouped(adc_channel, 2):
        number = number_to_2s_complement((high << 6) + (low >> 2), 14)
        values.append(number)

    temp_code = wired_frame[-8]
    temperature = temp_code * 1.13 - 46.8
    accelerometer = wired_frame[-7:-1]
    ed_measurement = wired_frame[-1]
    return values


class Plotter:
    def __init__(self, rangeval, minval, maxval):
        # You probably won't need this if you're embedding things in a tkinter plot...
        plt.ion()
        self.x = []

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        self.line1, = self.ax.plot(self.x, 'r', label='X')

        self.rangeval = rangeval
        self.ax.axis([0, rangeval, minval, maxval])
        self.plcounter = 0
        self.plotx = []

    def close(self):
        plt.close()

    def plotdata(self, new_values):
        self.x.append(new_values)
        self.plotx.append(self.plcounter)
        self.line1.set_ydata(self.x)
        self.line1.set_xdata(self.plotx)
        self.fig.canvas.draw()
        plt.pause(0.0001)
        self.plcounter = self.plcounter + 1

        if self.plcounter > self.rangeval:
            self.plcounter = 0
            self.plotx[:] = []
            self.x[:] = []


if __name__ == '__main__':
    ts = Controller()
    # header, payload, checksum = ts.get_status()
    # print(payload)

    ts.get_status()
    ts.get_relax_parameters()
    ts.get_relax_data()
    ts.reset_relax_variables()
    ts.turn_spi_on()
    # 5
    ts.turn_spi_off()
    # 5
    ts.set_rf_mode()
    # 5
    ts.turn_module_on()
    ts.turn_uc_on()

    plotter = Plotter(5000, -32700, 32700)

    while True:
        header, payload, checksum = ts.request_data()
        values = analyze_data_payload(payload)
        if values[0] != 64:
            for x in values:
                plotter.plotdata(x)
