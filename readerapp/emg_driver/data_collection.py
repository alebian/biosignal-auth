import threading
from enum import Enum

import numpy as np

import emg_driver.settings as settings

class DataCollectionThread(threading.Thread):
    def __init__(self, controller, storage, interpreted_storage, settings):
        super(DataCollectionThread, self).__init__()
        self.controller = controller
        self.get_values = True
        self.storage = storage
        self.interpreted_storage = interpreted_storage
        self.window_size = settings['window_size']
        self._encoder = EMGShieldEncoder(settings)

    def run(self):
        generator = self._filtered_data()
        while self.get_values:
            # packet = self.controller.read_data()
            # if packet.has_data():
            #     self.storage.extend(packet.get_channels()[0]) # We only care for channel0
            n = next(generator)
            self.storage.append(int(n))
            enc = self._encoder.encode(n)
            if enc is not None:
                self.interpreted_storage.append(int(enc))
        print(self._encoder.get_binary())
        self._encoder.clear()

    def stop(self):
        self.get_values = False

    def _filtered_data(self):
        i = 0
        values = np.empty(self.window_size, int)
        while True:
            i+=1
            if i < self.window_size:
                values[i] = self.controller.read_data().get_channels()[0][0]
                continue
            yield np.max(values)
            values[i % self.window_size] = self.controller.read_data().get_channels()[0][0]

class EMGShieldEncoder(object):
    class EncodingState(Enum):
        STARTING = 0
        ZERO = 1
        ONE = 0
        DONE = 0

    def __init__(self, settings):
        self.settings = settings
        self._prev = None
        self._zero_counter = 0
        self._state = EMGShieldEncoder.EncodingState.STARTING
        self._binary = []
        self._last = None

    @property
    def _spike_threshold(self):
        return self.settings['spike_threshold']

    @property
    def _zero_threshold(self):
        return self.settings['zero_threshold']

    @property
    def _zero_length(self):
        return self.settings['zero_length']

    def encode(self, value):
        if self._prev is not None:
            if self._prev < self._spike_threshold and value > self._spike_threshold:
                self._state = EMGShieldEncoder.EncodingState.ONE
                self._zero_counter = 0
                self._binary.append(1)
                self._last = len(self._binary)
                self._prev = value
                return 1
            if value < self._spike_threshold:
                self._zero_counter += 1
                if self._zero_counter >= self._zero_length:
                    self._binary.append(0)
                    self._zero_counter = 0
                    self._state = EMGShieldEncoder.EncodingState.ZERO
                    self._prev = value
                    self._zero_counter = 0
                    return 0
        self._prev = value

    def get_binary(self):
        return self._binary

    def clear(self):
        self._prev = None
        self._zero_counter = 0
        self._state = EMGShieldEncoder.EncodingState.STARTING
        self._binary = None
