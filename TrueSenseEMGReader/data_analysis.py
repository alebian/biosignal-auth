import matplotlib.pyplot as plt
import matplotlib.colors as colors

from data_collection import MOVEMENTS
from time_features import FEATURES
import file_helpers

PLACEMENT = 'extensor_carpis'
DATA_PATH = 'collected_data/alejandro/{}/**/*.json'.format(PLACEMENT)
DATA_MOVEMENTS = list(map(lambda x: x['key'], MOVEMENTS))


def _pre_process_signal(data):
    # TODO: filter signal
    return data


def extract_feature(feature_name, raw_data):
    return FEATURES[feature_name](
        _pre_process_signal(raw_data)
    )


if __name__ == '__main__':
    x = range(0, len(DATA_MOVEMENTS))

    for feature_name, feature in FEATURES.items():
        for idx, movement in enumerate(DATA_MOVEMENTS):
            plt.title('Feature {} for placement {}'.format(feature_name, PLACEMENT))

            files = file_helpers.files_matching(movement)
            features = list(
                map(lambda x: extract_feature(feature_name, file_helpers.get_values_from_file(x)), files)
            )

            plt.xticks(x, DATA_MOVEMENTS, rotation=45)
            for y in features:
                plt.scatter(idx, y, color=list(colors.cnames.values())[idx + 8])

        plt.show()
