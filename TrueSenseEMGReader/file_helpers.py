import glob
import json
import re


def get_all_files(path):
    return [x for x in glob.glob(path, recursive=True)]


def get_values_from_file(file):
    with open(file) as data_file:
        return json.load(data_file)['adc_values']


def files_matching(path, pattern):
    return [x for x in glob.glob(path, recursive=True) if re.search(pattern, x)]
