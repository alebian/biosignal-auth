import datetime
import json
import os
import time

from data_collection import DataCollectionThread
from emg_shield import EMGShieldController
from passwords import DataCollectionThread


class MovementCollectionThread(DataCollectionThread):
    def store_sample(self):
        folder = "collected_data/movements/{}".format(self.subject_name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

        data = self.controller.build_json_data(self.channels)
        filepath = "{}/{}_{}.json".format(folder, st, self.sample_n)
        with open(filepath, mode='w+') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)

samples = 10
name = 'Luis'

if __name__ == '__main__':
    controller = EMGShieldController()
    print("Bienvenido!")
    for x in range(1, samples + 1):
        collector = MovementCollectionThread(controller, name, x)

        print("Esta es la muestra {}".format(x))
        input("Presione enter para continuar...")
        collector.start()
        # To improve record key presses
        user = input()
        collector.stop()
