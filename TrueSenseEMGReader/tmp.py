import os
import json
import pywt

import matplotlib.pyplot as plt

from plotters import DynamicPlotter


TEST_FILES_DIR = './collected_data/alejandro'
def hand_files():
    for num in range (1, 6):
        yield json.load(open(os.path.join(TEST_FILES_DIR, 'close_hand_{0}_2017-10-13.json'.format(num))))['adc_values']


def finger_files():
    for num in range (1, 6):
        yield json.load(open(os.path.join(TEST_FILES_DIR, 'finger_1_{0}_2017-10-13.json'.format(num))))['adc_values']


for data in hand_files():
    coefs = pywt.wavedec(data=data, wavelet='db4', level=4)
    plt.plot(coefs[0])
    plt.show()

for data in finger_files():
    coefs = pywt.wavedec(data=data, wavelet='db4', level=4)
    plt.plot(coefs[0])
    plt.show()


