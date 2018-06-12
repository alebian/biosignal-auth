import re
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import pywt

from time_features import FEATURES
import noise_reduction
import file_helpers

ale_values = list(map(lambda x: file_helpers.get_values_from_file(x), file_helpers.get_all_files('collected_data/passwords/alejandro/**/*.json')))
luis_values = list(map(lambda x: file_helpers.get_values_from_file(x), file_helpers.get_all_files('collected_data/passwords/luis/**/*.json')))


def _pre_process_signal(values):
    return noise_reduction.filter_emg_signal(values)


def extract_feature(feature_name, raw_data):
    return FEATURES[feature_name](
        _pre_process_signal(raw_data)
    )


if __name__ == '__main__':
    feature_idx = 0

    for feature_name, feature in FEATURES.items():
        # Para todas las combinaciones de wavelet, mode y threshold ver en cual el promedio de las features esta mas alejado del resto
        ale_features = list(map(lambda x: extract_feature(feature_name, x), ale_values))
        luis_features = list(map(lambda x: extract_feature(feature_name, x), luis_values))

        # x = range(0, len(values))

        # plt.xticks(x, features, rotation=45)
        for y in ale_features:
            plt.scatter(feature_idx, y, color='red')

        for y in luis_features:
            plt.scatter(feature_idx, y, color='blue')

        feature_idx += 1

    plt.show()