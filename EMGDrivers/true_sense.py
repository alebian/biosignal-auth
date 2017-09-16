from serial import Serial, SerialException
from logger import get_logger

import settings

SYNC_BYTE = 0x33


class Controller:
    def __init__(self):
        self._logger = get_logger()
        # Try all known ports
        for port in settings.POSSIBLE_PORTS:
            try:
                self.serial = Serial(port=port, baudrate=settings.BAUDRATE, timeout=3)
                self._logger.info(str.format("Using device in port: {}", port))
                break
            except SerialException as e:
                continue

    def set_up(self):
        self.get_status()
        self.get_relax_parameters()
        self.get_relax_data()
        self.reset_relax_variables()
        self.turn_spi_on()
        # 5
        self.turn_spi_off()
        # 5
        self.set_rf_mode()
        # 5
        self.turn_module_on()
        self.turn_uc_on()

    def request_data(self):
        return self.basic_request(0x10, payload=[0x00], msg='Request wireless truesense data from unicon')

    def get_status(self):
        return self.basic_request(0x10, payload=[0x01], msg='Gets the plugged in UC status')

    def get_measure(self):
        return self.basic_request(0x10, payload=[0x10], msg='Request wireless measurement of current channel from slave')

    def get_relax_data(self):
        return self.basic_request(0x14, payload=[0x00], msg='Get the relax state data')

    def reset_relax_variables(self):
        return self.basic_request(0x14, payload=[0x02], msg='Reset the variables related to relax state in controller')

    def get_relax_parameters(self):
        return self.basic_request(0x14, payload=[0x04], msg='Get the parameters used in calculating the Relax state')

    def set_rf_mode(self):
        return self.basic_request(0x20, payload=[0x04], msg='Sets the plugged in truesense RF Mode')

    def turn_spi_on(self):
        return self.basic_request(0x20, payload=[0x0B], msg='Turn controller microSD SPI interface on')

    def turn_module_on(self):
        return self.basic_request(0x20, payload=[0x21], msg='Turn module on through unified controller')  #

    def turn_uc_on(self):
        return self.basic_request(0x20, payload=[0x23], msg='Set controller to on-state where it will turn on')

    def turn_spi_off(self):
        return self.basic_request(0x20, payload=[0x24], msg='Turn controller microSD SPI interface off')

    def basic_request(self, data_code, payload=[], msg='About to send a packet to the device'):
        """
        This method sends a generic packet to the device
        This packet is defined by the Link protocol and the Wired frame

            @params:
                * data_code: data code defined int the Wired Frame definition
                * payload [List]: also defined in the Wired Frame definition, contains sud_data_code
        """
        self._logger.debug(msg)
        packet = Packet.create_packet(data_code, payload)
        self._write_packet(packet)
        return self._read_packet()

    def _write_packet(self, packet):
        self._logger.debug(str.format('About to write a packet: {}', packet))
        self.serial.write(packet)

    def _read_packet(self, src=None):
        if src == None:
            src = self.serial
        return Packet.read_from_stream(src, self._logger)


"""
    Packet classes
"""


def grouped(iterable, n):
    return zip(*[iter(iterable)] * n)


def number_to_2s_complement(number, n):
    return number if (number >> n - 1) == 0 else number - (1 << n)


class Packet:
    def create_packet(data_code, payload):
        wired = WiredPacket(data_code, payload)
        return LinkPacket(wired.to_list()).to_list()

    def read_from_stream(stream, logger):
        logger.debug('About to read a packet...')
        header = stream.read(4)
        if header[0] != SYNC_BYTE or header[1] != SYNC_BYTE:
            logger.error('There was an error with the packet SYNC bytes')
            logger.debug('Sync bytes were:')
            logger.debug(header[0])
            logger.debug(header[1])
            raise SyncError

        payload_length = (header[2] << 8) + header[3]
        payload = list(stream.read(payload_length))
        if payload_length != len(payload):
            logger.error('There was an error with the packet payload length')
            logger.debug('Payloads lengths were:')
            logger.debug(payload_length)
            logger.debug(len(payload))
            raise SizeDoesNotMatchError('payload')

        checksum = stream.read(2)
        checksum = (checksum[0] << 8) + checksum[1]
        if sum(payload) != checksum:
            logger.error('There was an error with the packet checksum')
            logger.debug('Payload was:')
            logger.debug(payload)
            logger.debug(str.format('Calculated checksum was: {}', sum(payload)))
            logger.debug(str.format('Provided checksum was: {}', checksum))
            raise ChecksumError

        return (list(header), payload, checksum)


class LinkPacket():
    def __init__(self, payload=[]):
        self.payload = payload

    def to_list(self):
        return [SYNC_BYTE, SYNC_BYTE] + self._get_length() + self.payload + self._get_checksum()

    def _get_length(self):
        high_byte = ((len(self.payload)) >> 8) & 0xff
        low_byte = (len(self.payload)) & 0xff
        return [high_byte, low_byte]

    def _get_checksum(self):
        chk = sum(self.payload)
        high_byte = chk >> 8
        low_byte = chk
        return [high_byte, low_byte]


class WiredPacket():
    def __init__(self, data_code, payload=[]):
        self.data_code = data_code
        self.payload = payload

    def to_list(self):
        return [self.data_code] + self.payload


# This class represents data defined in the Wired Frame Definition as: Interpreted/Fixed Received Wireless TrueSense Data
class WirelessDataPacket():
    # Values used for scale
    VALUE_MAX = 32767 # max number to read
    VALUE_MIN = -32768 # min number to read
    VALUE_RANGE = VALUE_MAX - VALUE_MIN
    PHYSICAL_MAX = 800 # max physical measure [uV]
    PHYSICAL_MIN = -800 # min physical measure [uV]
    PHYSICAL_RANGE = PHYSICAL_MAX - PHYSICAL_MIN
    # Constants
    HAS_DATA = 0x01
    NO_DATA = 0x40
    VALID_DATA_CODE = 0x01
    SAMPLE_QUALITY_MASK = 0x03
    CORRUPTED_DATA = 3


    def __init__(self, payload, scale=False):
        self.payload = payload
        self.scale = scale
        self._logger = get_logger()
        self.adc_values = []
        self._analyze()

    def max_value(scale):
        return WirelessDataPacket.PHYSICAL_MAX if scale else WirelessDataPacket.VALUE_MAX

    def min_value(scale):
        return WirelessDataPacket.PHYSICAL_MIN if scale else WirelessDataPacket.VALUE_MIN

    def battery_state(self):
        if self.battery == 1:
            self._logger.info('Battery level above 3.15V')
            return True
        else:
            self._logger.info('Battery level below 3.15V')
            return False

    def has_data(self):
        if self.payload[0] == WirelessDataPacket.HAS_DATA:
            return True
        elif self.payload[0] == WirelessDataPacket.NO_DATA:
            self._logger.debug('No data found in packet')
        else:
            self._logger.error('Error in data')

        return False

    def _analyze(self):
        if self.has_data():
            self._decode_data_codes()
            self._decode_timestamp()
            self._decode_paired_device_number()
            self._decode_miscellaneous_data()
            self._decode_adc_values()
            self._decode_temperature()
            self._decode_accelerometer()
            self._decode_ed_measurement()

    def _decode_data_codes(self):
        self.data_code = self.payload[0]
        if self.data_code != WirelessDataPacket.VALID_DATA_CODE:
            raise DataCodeError(WirelessDataPacket.VALID_DATA_CODE, self.data_code)

        self.sub_data_code = self.payload[1]
        if self.sub_data_code != WirelessDataPacket.VALID_DATA_CODE:
            raise DataCodeError(WirelessDataPacket.VALID_DATA_CODE, self.sub_data_code)

    def _decode_timestamp(self):
        self.timestamp = self.payload[2:8]

    def _decode_paired_device_number(self):
        self.paired_device_number = self.payload[8]

    def _decode_miscellaneous_data(self):
        # 0 010 000 1
        self.miscellaneous_data = self.payload[9]
        self.battery = self.miscellaneous_data & 0x01

    def _decode_adc_values(self):
        adc_channel = self.payload[10:-8]
        for high, low in grouped(adc_channel, 2):
            data_corruption = low & WirelessDataPacket.SAMPLE_QUALITY_MASK
            if data_corruption == WirelessDataPacket.CORRUPTED_DATA:
                self._logger.debug('Corrupted data found')
                break
            number = number_to_2s_complement((high << 6) + (low >> 2), 14)
            number = self._scale(number)
            self.adc_values.append(number)

    def _decode_temperature(self):
        self.temperature = self.payload[-8]

    def _decode_accelerometer(self):
        self.accelerometer = self.payload[-7:-1]

    def _decode_ed_measurement(self):
        self.ed_measurement = self.payload[-1]

    def _scale(self, number):
        scaled = number
        if self.scale:
            scaled = (((number - WirelessDataPacket.VALUE_MIN) * WirelessDataPacket.PHYSICAL_RANGE) / WirelessDataPacket.VALUE_RANGE) + WirelessDataPacket.PHYSICAL_MIN
        return scaled


"""
    Exceptions
"""


class SyncError(Exception):
    def __init__(self, value='SYNC bytes do not match'):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SizeDoesNotMatchError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return format("Size of %s does not match", self.value)


class ChecksumError(Exception):
    def __init__(self, value='Checksum does not validate data'):
        self.value = value

    def __str__(self):
        return repr(self.value)

class DataCodeError(Exception):
    def __init__(self, expected, got):
        self.expected = expected
        self.got = got

    def __str__(self):
        return repr(str.format('Invalid data code. Expected {} but received {}', self.expected, self.got))