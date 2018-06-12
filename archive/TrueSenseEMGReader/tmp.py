import os
import json
import pywt

import matplotlib.pyplot as plt
import time_features



TEST_FILES_DIR = './collected_data/alejandro'
def hand_files():
    for num in range (1, 6):
        yield json.load(open(os.path.join(TEST_FILES_DIR, 'close_hand_{0}_2017-10-13.json'.format(num))))['adc_values']


def finger_files(finger):
    for num in range (1, 6):
        yield json.load(open(os.path.join(TEST_FILES_DIR, 'finger_{0}_{1}_2017-10-13.json'.format(finger, num))))['adc_values']


colors = ['red', 'green', 'blue', 'yellow', 'pink']

for data in hand_files():
    coefs = pywt.wavedec(data=data, wavelet='haar', level=5)
    plt.title("Hand")
    plt.plot(coefs[0])
    # plt.plot(time_features.willison_amplitude(coefs[0],20), time_features.zero_crossing(coefs[0], 10), marker='x', color=colors[finger])
    plt.show()

for finger in range(0,5):
    for data in finger_files(finger):
        coefs = pywt.wavedec(data=data, wavelet='haar', level=5)
        plt.title("Finger {0}".format(finger))
        plt.plot(coefs[0])
        #plt.plot(time_features.willison_amplitude(coefs[0],20), time_features.zero_crossing(coefs[0], 10), marker='x', color=colors[finger])
        plt.show()


