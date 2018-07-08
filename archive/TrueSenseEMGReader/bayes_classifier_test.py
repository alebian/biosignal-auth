import math
import random
import os
import json
import numpy as np

import noise_reduction
import file_helpers
from time_features import FEATURES

TEST_FILES_DIR = './collected_data/alejandro/flexor_carpi'
def finger_files(finger):
    for num in range (1, 20):
        yield json.load(open(os.path.join(TEST_FILES_DIR, 'finger_{0}_{1}_2017-10-29.json'.format(finger, num))))['adc_values']

luis_files = list(map(lambda x: file_helpers.get_values_from_file(x), file_helpers.get_all_files('collected_data/passwords/luis/**/*.json')))

people = {}


def _calculate_probability(x, mean, stdev):
    exponent = math.exp(-(math.pow(x - mean, 2) / (2 * math.pow(stdev, 2))))
    return (1 / (math.sqrt(2 * math.pi) * stdev)) * exponent


def prediction(signal, feature_name, mean, std):
    return _calculate_probability(FEATURES[feature_name](signal), mean, std)


def train(train_data):
    result = {}

    # Remove noise from signals
    data_without_noise = list(map(lambda x: noise_reduction.filter_emg_signal(x), train_data))

    for feature_name, feature in FEATURES.items():
        calculated_features = list(map(lambda x: FEATURES[feature_name](x), data_without_noise))

        result[feature_name] = {
            'mean': np.mean(calculated_features),
            'std': np.std(calculated_features),
        }

    return result


def split_dataset(dataset, splitRatio=0.67):
    train_size = int(len(dataset) * splitRatio)
    train_set = []
    copy = list(dataset)
    while len(train_set) < train_size:
        index = random.randrange(len(copy))
        train_set.append(copy.pop(index))
    return [train_set, copy]


if __name__ == '__main__':
    split_ratio = 0.3

    finger_0_data = list(finger_files(0))
    finger_1_data = list(finger_files(1))
    finger_2_data = list(finger_files(2))
    finger_3_data = list(finger_files(3))
    finger_4_data = list(finger_files(4))

    # train_data, test_data = split_dataset(finger_0_data, split_ratio)
    train_data = finger_0_data
    test_data = finger_0_data

    trainings = train(train_data)

    for feature_name, data in trainings.items():
        predictions = list(map(lambda signal: prediction(signal, feature_name, data['mean'], data['std']), test_data))
        print('Average prediction for {} is {:.2f}%'.format(feature_name, np.mean(predictions) * 100))
