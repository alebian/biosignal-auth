import json

import settings
from plotters import DynamicAccelerometerPlotter
from plotters import DynamicPlotter
from true_sense import Controller, WirelessDataPacket


if __name__ == '__main__':
    size = 1600

    truesense_controller = Controller()
    truesense_controller.set_up()

    adc_plotter = DynamicPlotter(
        x_range=size,
        min_val=WirelessDataPacket.PHYSICAL_MIN,
        max_val=WirelessDataPacket.PHYSICAL_MAX
    )

    # temperature_plotter = DynamicPlotter(x_range=200, min_val=25, max_val=40, title='Temperature', y_label='Celsius degrees', color='b')
    # accelerometer_plotter = DynamicAccelerometerPlotter()

    adc_values = []

    while len(adc_values) < size:
        packet = truesense_controller.request_data()

        if packet.has_data():
            adc_values = adc_values + packet.adc_values

            for x in packet.adc_values:
                adc_plotter.plotdata(x)
            # temperature_plotter.plotdata(packet.temperature)
            # accelerometer_plotter.plotdata(packet.accelerometer)

    # truesense_controller.save_values_to_file(
    #     settings.TEMP_SCAN,
    #     truesense_controller.build_data_json(adc_values)
    # )
    # print('Saved to file')
