import time
import datetime
import os

from true_sense import Controller, WirelessDataPacket
from plotters import DynamicPlotter

DATA_FOLDER = "collected_data"
PERSON_NAME = "alejandro"

MOVEMENTS = [
    { "key": "close_hand", "name": "Cerrar mano",         "desc": "Comenzando con la mano completamente abierta, cierrela por un instante y vuelva a abrirla" },
    { "key": "finger_0",   "name": "Cerrar dedo gordo",   "desc": "Comenzando con la mano completamente abierta, cierre el dedo gordo por completo" },
    { "key": "finger_1",   "name": "Cerrar dedo indice",  "desc": "Comenzando con la mano completamente abierta, cierre el dedo indice por completo" },
    { "key": "finger_2",   "name": "Cerrar dedo mayor",   "desc": "Comenzando con la mano completamente abierta, cierre el dedo mayor por completo" },
    { "key": "finger_3",   "name": "Cerrar dedo anular",  "desc": "Comenzando con la mano completamente abierta, cierre el dedo anular por completo" },
    { "key": "finger_4",   "name": "Cerrar dedo meñique", "desc": "Comenzando con la mano completamente abierta, cierre el dedo meñique por completo" }
]

NUMBER_OF_SAMPLES = 5
SAMPLE_SIZE = 400
COUNTDOWN = 3

SAMPLE_TYPE = "EMG"
DEVICE = "TrueSense kit"

def prompt_continue():
    input("Presione enter para continuar...")

def take_sample(controller, plotter, movement, sample_number):
    folder = "{}/{}".format(DATA_FOLDER, PERSON_NAME)
    if not os.path.exists(folder):
        os.makedirs(folder)
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    data_file = "{}/{}_{}_{}.json".format(folder, movement["key"], sample_number, st)

    print("       Movimiento: {}".format(movement["name"]))
    print("      Descripcion: {}".format(movement["desc"]))
    print("Numero de muestra: {} de {}".format(sample_number, NUMBER_OF_SAMPLES))
    prompt_continue()
    print("Comienza a realizar el movimiento a la cuenta de {}".format(COUNTDOWN))
    for x in range(1, COUNTDOWN + 1):
        print(x)
        time.sleep(1)
    print("Ahora!")

    take_sample = True
    adc_values = None
    plotted = 0
    while take_sample:
        adc_values = []
        while len(adc_values) < SAMPLE_SIZE:
            packet = controller.request_data()
            if packet.has_data():
                adc_values = adc_values + packet.adc_values

                for x in packet.adc_values:
                    if plotted < SAMPLE_SIZE:
                        plotter.plotdata(x)
                        plotted += 1
        plotted = 0

        print("Muestra tomada correctamente")
        again = input("Desea tomar la muestra nuevamente? [y/N]")
        if again != "y":
            take_sample = False

    controller.save_values_to_file(
        data_file,
        controller.build_data_json(adc_values)
    )
    print("Muestra guardada correctamente")
    print("Gracias!")


if __name__ == '__main__':
    truesense_controller = Controller()
    truesense_controller.set_up()

    adc_plotter = DynamicPlotter(
        x_range=SAMPLE_SIZE,
        min_val=WirelessDataPacket.PHYSICAL_MIN,
        max_val=WirelessDataPacket.PHYSICAL_MAX
    )

    print("Bienvenido {}! Vamos a tomar muestras {} usando el {}".format(PERSON_NAME, SAMPLE_TYPE, DEVICE))
    print("Se mostraran varios movimientos y se tomaran {} muestras para cada uno".format(NUMBER_OF_SAMPLES))
    print("Podra ver graficamente los valores tomados todo el tiempo pero las muestras se tomaran cuando se le informe\n".format(
        NUMBER_OF_SAMPLES))

    prompt_continue()

    for movement in MOVEMENTS:
        for n in range(1, NUMBER_OF_SAMPLES + 1):
            take_sample(truesense_controller, adc_plotter, movement, n)
