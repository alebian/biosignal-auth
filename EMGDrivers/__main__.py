from true_sense import Controller, WirelessDataPacket
from dynamic_plotter import DynamicPlotter


if __name__ == '__main__':
    ts = Controller()

    ts.set_up()

    scale = True
    min_val = WirelessDataPacket.min_value(scale)
    max_val = WirelessDataPacket.max_value(scale)

    plotter = DynamicPlotter(range=5000, min_val=min_val, max_val=max_val)

    while True:
        header, payload, checksum = ts.request_data()
        packet = WirelessDataPacket(payload, scale=scale)

        for x in packet.adc_values:
            plotter.plotdata(x)
