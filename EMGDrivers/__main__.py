from true_sense import Controller
from dynamic_plotter import DynamicPlotter


def grouped(iterable, n):
    return zip(*[iter(iterable)] * n)


def number_to_2s_complement(number, n):
    return number if (number >> n - 1) == 0 else number - (1 << n)


def analyze_data_payload(wired_frame):
    if wired_frame[0] == 64:
        return wired_frame

    values = []
    print(wired_frame)
    data_code = wired_frame[0]
    sub_data_code = wired_frame[1]
    timestamp_values = wired_frame[2:8]

    paired_device_number = wired_frame[8]
    miscellaneous_data = wired_frame[9]
    # 0 010 000 1
    adc_channel = wired_frame[10:-8]

    for high, low in grouped(adc_channel, 2):
        number = number_to_2s_complement((high << 6) + (low >> 2), 14)
        values.append(number)

    temp_code = wired_frame[-8]
    temperature = temp_code * 1.13 - 46.8
    accelerometer = wired_frame[-7:-1]
    ed_measurement = wired_frame[-1]
    return values


if __name__ == '__main__':
    ts = Controller()

    ts.get_status()
    ts.get_relax_parameters()
    ts.get_relax_data()
    ts.reset_relax_variables()
    ts.turn_spi_on()
    # 5
    ts.turn_spi_off()
    # 5
    ts.set_rf_mode()
    # 5
    ts.turn_module_on()
    ts.turn_uc_on()

    plotter = DynamicPlotter(range=5000, min_val=-32700, max_val=32700)

    while True:
        header, payload, checksum = ts.request_data()
        values = analyze_data_payload(payload)
        print(values)
        if values[0] != 64:
            for x in values:
                plotter.plotdata(x)
