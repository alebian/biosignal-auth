import time

from true_sense import Controller
import logger
from true_sense import Packet


def interpret_file_bytes(stream):
    rest = []

    while stream.has_next():
        rest.append(Packet.read_from_stream(stream, logger.get_logger()))

    return rest


def basic(code, sub_code, msg):
    print(msg)
    header, payload, checksum = ts.basic_request(code, sub_code)
    print(header)
    print(payload)


if __name__ == '__main__':
    ts = Controller()
    # header, payload, checksum = ts.get_status()
    # print(payload)

    basic(0x10, 0x01, 'Gets the plugged in UC status')
    basic(0x14, 0x04, 'Get the parameters used in calculating the Relax state')
    basic(0x14, 0x00, 'Get the relax state data')
    basic(0x14, 0x02, 'Reset the variables related to relax state in controller')
    basic(0x20, 0x0B, 'Turn controller microSD SPI interface on')
    # 5
    basic(0x20, 0x24, 'Turn controller microSD SPI interface off')
    # 5
    basic(0x20, 0x04, 'Sets the plugged in truesense RF Mode')
    # 5
    basic(0x20, 0x21, 'Turn module on through unified controller') #
    basic(0x20, 0x23, 'Set controller to on-state where it will turn on')

    while True:
        basic(0x10, 0x00, 'Request wireless truesense data from unicon')
        time.sleep(1)
