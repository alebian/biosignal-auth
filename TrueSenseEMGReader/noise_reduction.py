import matplotlib.pyplot as plt
import numpy as np
import pywt

import file_helpers
from time_features import FEATURES

finger_file = 'collected_data/alejandro/extensor_carpis/finger_1_1_2017-10-30.json'
password_file = 'collected_data/passwords/alejandro/2018-03-18_1.json'

ale_files = file_helpers.get_all_files('collected_data/passwords/alejandro/**/*.json')
luis_files = file_helpers.get_all_files('collected_data/passwords/luis/**/*.json')


def filter_emg_signal(values, wavelet='db1', threshold_mode='hard', threshold_value=3.0, wavelet_level=None):
    if wavelet_level is not None:
        coefs = pywt.wavedec(values, wavelet, level=wavelet_level)
        inverse = pywt.waverec(
            list(map(lambda x: pywt.threshold(x, threshold_value, threshold_mode), coefs)),
            wavelet
        )
    else:
        (cA, cD) = pywt.dwt(values, wavelet)
        inverse = pywt.idwt(
            pywt.threshold(cA, threshold_value, threshold_mode),
            pywt.threshold(cD, threshold_value, threshold_mode),
            wavelet
        )

    return inverse


def plot(original_signal, reduced_signal):
    original_x = range(0, len(original_signal))
    filtered_x = range(0, len(reduced_signal))

    plt.plot(original_x, original_signal, color='red')
    plt.plot(filtered_x, reduced_signal, color='blue')

    plt.show()

# Feature: integrated_emg best variant is: sym5 - hard - 10.9 - None
# Feature: mean_absolute_value best variant is: sym5 - hard - 10.9 - None
# Feature: simple_square_integral best variant is: db1 - hard - 9.3 - None
# Feature: variance_of_emg best variant is: db1 - hard - 6.0 - None
# Feature: root_mean_square best variant is: db2 - hard - 10.9 - None
# Feature: waveform_length best variant is: bior6.8 - hard - 9.1 - 4
def _calculate_average_features():
    result = {
        'ale':  {
            'values': list(map(lambda x: file_helpers.get_values_from_file(x), ale_files)),
            'features': {}
        },
        'luis': {
            'values': list(map(lambda x: file_helpers.get_values_from_file(x), luis_files)),
            'features': {}
        }
    }

    wavelets = ['sym5', 'bior6.8', 'db1', 'db2']
    threshold_modes = ['hard', 'soft']
    thresholds = np.arange(0.1, 11.0, 0.1)
    wavelet_levels = [None, 4]

    # First get the features without noise reduction
    for feature_name, feature in FEATURES.items():
        for person, info in result.items():
            features = list(map(lambda x: FEATURES[feature_name](x), info['values']))
            if feature_name not in info['features']:
                info['features'][feature_name] = {}
            info['features'][feature_name]['raw'] = np.mean(features)

    # Now calculate the features with noise reduction
    for wavelet in wavelets:
        for threshold_mode in threshold_modes:
            for threshold in thresholds:
                for wavelet_level in wavelet_levels:
                    # Calculate the averages
                    for feature_name, feature in FEATURES.items():
                        for person, info in result.items():
                            features = list(
                                map(
                                    lambda filtered_signal: FEATURES[feature_name](filtered_signal),
                                    map(
                                        lambda original_signal: filter_emg_signal(
                                            original_signal, wavelet=wavelet, threshold_mode=threshold_mode, threshold_value=threshold, wavelet_level=wavelet_level
                                        ),
                                        info['values']
                                    )
                                )
                            )
                            info['features'][feature_name]['{} - {} - {} - {}'.format(wavelet, threshold_mode, threshold, wavelet_level)] = np.mean(features)

    people = list(result.keys())
    features = list(FEATURES.keys())
    variants = list(result[people[0]]['features'][features[0]].keys())

    for feature in features:
        max_diff = 0
        max_variant = None

        for variant in variants:
            averages = []
            for person in people:
                averages.append(result[person]['features'][feature][variant])

            min_diff = _find_min_diff(averages)
            if min_diff > max_diff:
                max_diff = min_diff
                max_variant = variant

        print('Feature: {} best variant is: {}'.format(feature, max_variant))


def _find_min_diff(arr):
    # Sort array in non-decreasing order
    arr = sorted(arr)
    # Initialize difference as infinite
    diff = 10 ** 20
    # Find the min diff by comparing adjacent pairs in sorted array
    for i in range(len(arr) - 1):
        if arr[i + 1] - arr[i] < diff:
            diff = arr[i + 1] - arr[i]

    return diff


if __name__ == '__main__':
    #_calculate_average_features()

    original_signal = file_helpers.get_values_from_file(password_file)
    filtered_signal = filter_emg_signal(original_signal, wavelet='sym5', threshold_value=3.0)
    plot(original_signal, filtered_signal)


