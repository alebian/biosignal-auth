import json
import glob
import re
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from time_features import FEATURES

DATA_PATH = 'collected_data/passwords/alejandro/**/*.json'

files = [x for x in glob.glob(DATA_PATH, recursive=True)]

def get_values_from_file(file):
    with open(file) as data_file:
        return json.load(data_file)['adc_values']

def _pre_process_signal(data):
    # TODO: filter signal
    return data

def extract_feature(feature_name, raw_data):
    return FEATURES[feature_name](
        _pre_process_signal(raw_data)
    )

if __name__ == '__main__':
    count = 0

    for feature_name, feature in FEATURES.items():
        plt.title('Feature {}'.format(feature_name))

        values = list(map(lambda x: get_values_from_file(x), files))
        features = list(map(lambda x: extract_feature(feature_name, x), values))
        x = range(0, len(values))

        plt.xticks(x, features, rotation=45)
        for y in features:
            plt.scatter(count, y, color=list(colors.cnames.values())[count + 8])

        count += 1

        plt.show()