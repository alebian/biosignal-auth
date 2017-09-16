from plotters import DynamicAccelerometerPlotter
from plotters import DynamicPlotter
from true_sense import Controller, WirelessDataPacket

if __name__ == '__main__':
    truesense_controller = Controller()
    truesense_controller.set_up()

    scale = True
    adc_plotter = DynamicPlotter(
        x_range=2000,
        min_val=WirelessDataPacket.VALUE_MIN,
        max_val=WirelessDataPacket.VALUE_MAX
    )
    if scale:
        adc_plotter = DynamicPlotter(
            x_range=2000,
            min_val=WirelessDataPacket.PHYSICAL_MIN,
            max_val=WirelessDataPacket.PHYSICAL_MAX
        )

    temperature_plotter = DynamicPlotter(x_range=200, min_val=25, max_val=40, title='Temperature',
                                         y_label='Celsius degrees', color='b')
    accelerometer_plotter = DynamicAccelerometerPlotter()

    while True:
        data_packet = truesense_controller.request_data()
        packet = WirelessDataPacket(data_packet.payload, scale=scale)

        if packet.has_data():
            for x in packet.adc_values:
                adc_plotter.plotdata(x)
            temperature_plotter.plotdata(packet.temperature)
            accelerometer_plotter.plotdata(packet.accelerometer)
