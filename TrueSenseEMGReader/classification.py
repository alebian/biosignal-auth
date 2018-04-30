import math
import random
import numpy as np

import noise_reduction
import file_helpers
from time_features import FEATURES

ale_files = list(map(lambda x: file_helpers.get_values_from_file(x), file_helpers.get_all_files('collected_data/passwords/alejandro/**/*.json')))
luis_files = list(map(lambda x: file_helpers.get_values_from_file(x), file_helpers.get_all_files('collected_data/passwords/luis/**/*.json')))

people = {}


def _calculate_probability(x, mean, stdev):
    exponent = math.exp(-(math.pow(x - mean, 2) / (2 * math.pow(stdev, 2))))
    return (1 / (math.sqrt(2 * math.pi) * stdev)) * exponent


def prediction(person, signal):
    probabilities = []
    for feature_name, feature in FEATURES.items():
        feat = FEATURES[feature_name](signal)
        mean = people[person][feature_name]['mean']
        std = people[person][feature_name]['std']
        probabilities.append(_calculate_probability(feat, mean, std))
    return probabilities


def train(person, train_data):
    # Add person if missing
    if person not in people:
        people[person] = {}

    # Remove noise from signals
    data_without_noise = list(map(lambda x: noise_reduction.filter_emg_signal(x), train_data))

    for feature_name, feature in FEATURES.items():
        calculated_features = list(map(lambda x: FEATURES[feature_name](x), data_without_noise))

        people[person][feature_name] = {
            'mean': np.mean(calculated_features),
            'std': np.std(calculated_features),
        }


def split_dataset(dataset, splitRatio=0.67):
    train_size = int(len(dataset) * splitRatio)
    train_set = []
    copy = list(dataset)
    while len(train_set) < train_size:
        index = random.randrange(len(copy))
        train_set.append(copy.pop(index))
    return [train_set, copy]


if __name__ == '__main__':
    split_ratio = 0.2
    datasets = [
        ['ale', ale_files],
        ['luis', luis_files],
    ]
    for data in datasets:
        train_data, test_data = split_dataset(data[1], split_ratio)
        train(data[0], train_data)
        predictions = list(map(lambda x: prediction(data[0], x), test_data))
        print('Average prediction for {} is {:.2f}%'.format(data[0], np.mean(predictions) * 100))
