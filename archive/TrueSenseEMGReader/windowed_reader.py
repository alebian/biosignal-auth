from true_sense import Controller, WirelessDataPacket
from plotters import DynamicPlotter

values = []
MAX_SIZE = 10000
WINDOW_STEP = 10
WINDOW_LENGTH = 100
start = 0
truesense_controller = Controller()
truesense_controller.set_up()

adc_plotter = DynamicPlotter(
    x_range=MAX_SIZE,
    min_val=WirelessDataPacket.PHYSICAL_MIN,
    max_val=WirelessDataPacket.PHYSICAL_MAX
)


while True:
    packet = truesense_controller.request_data()
    if packet.has_data():
        values = values + packet.adc_values
        for x in packet.adc_values:
                adc_plotter.plotdata(x)

        while len(values) > start + WINDOW_LENGTH:
            window = values[start:start+WINDOW_LENGTH]
            print("NEW WINDOW")
            print("MAX: " + max(window))
            start += WINDOW_STEP
