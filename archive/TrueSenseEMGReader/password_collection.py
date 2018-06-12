import threading
import os
import datetime
import time

from true_sense import Controller

person = 'luis'
samples = 20


class TrueSenseThread(threading.Thread):
    def __init__(self, controller, adc_values, accelerometer_values):
        super(TrueSenseThread, self).__init__()
        self.controller = controller
        self.adc_values = adc_values
        self.accelerometer_values = accelerometer_values
        self.get_values = True

    def run(self):
        while self.get_values:
            packet = self.controller.request_data()
            if packet.has_data():
                for x in packet.adc_values:
                    self.adc_values.append(x)
                self.accelerometer_values.append(packet.accelerometer)

    def stop(self):
        self.get_values = False


def store_adc_values(controller, adc_values, accelerometer_values, x):
    folder = "collected_data/passwords/{}".format(person)
    if not os.path.exists(folder):
        os.makedirs(folder)
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

    controller.save_values_to_file(
        "{}/{}_{}.json".format(folder, st, x),
        controller.build_data_json(
            adc=adc_values,
            x=[x[0] for x in accelerometer_values],
            y=[x[1] for x in accelerometer_values],
            z=[x[2] for x in accelerometer_values]
        )
    )


if __name__ == '__main__':
    truesense_controller = Controller()
    truesense_controller.set_up()

    print("Bienvenido!")

    for x in range(1, samples + 1):
        adc_values = []
        accelerometer_values = []

        truesense = TrueSenseThread(truesense_controller, adc_values, accelerometer_values)

        print("Esta es la muestra {}".format(x))
        input("Presione enter para continuar...")

        print("Ingrese el nombre de usuario 'test@test.com' y luego presione enter:")
        truesense.start()
        # To improve record key presses
        user = input()
        print("Ingrese la contraseña 'esta es una contraseña muy larga' y luego presione enter:")
        password = input()
        truesense.stop()
        # Finish recording key presses
        store_adc_values(truesense_controller, adc_values, accelerometer_values, x)
