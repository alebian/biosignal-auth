import os
import time
import datetime
import json

from data_collection import DataCollectionThread

class PasswordCollectionThread(DataCollectionThread):
    def store_sample(self):
        folder = "collected_data/passwords/{}".format(self.subject_name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

        data = self.controller.build_json_data(self.channels)
        filepath = "{}/{}_{}.json".format(folder, st, self.sample_n)
        with open(filepath, mode='w+') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
