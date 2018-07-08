import re
import json
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import pywt

from time_features import FEATURES
import noise_reduction
import file_helpers

def _pre_process_signal(values):
    return noise_reduction.filter_emg_signal(values)


def extract_feature(feature_name, raw_data):
    return FEATURES[feature_name](
        _pre_process_signal(raw_data)
    )

TEST_FILES_DIR = './collected_data/alejandro/flexor_carpi'
def finger_files(finger):
    for num in range (1, 20):
        yield json.load(open(os.path.join(TEST_FILES_DIR, 'finger_{0}_{1}_2017-10-29.json'.format(finger, num))))['adc_values']


if __name__ == '__main__':
    feature_name = 'simple_square_integral'
    feature = FEATURES[feature_name]

    for finger in range(0, 5):
        values = list(finger_files(finger))
        features = list(map(lambda x: extract_feature(feature_name, x), values))
        for y in features:
            plt.scatter('finger {}'.format(finger), y, color='red')

    plt.title("Feature: {}\nMovimiento: cerrar dedo".format(feature_name), fontsize=16)
    plt.show()
