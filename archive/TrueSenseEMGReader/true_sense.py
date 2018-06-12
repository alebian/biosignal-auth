import datetime
import json
import statistics
import time

from serial import Serial, SerialException

from emg import EMGController, DataPacket
import settings
from logger import get_logger


class Controller:
    def __init__(self, scale=True):
        self.scale = scale
        self._logger = get_logger()
        # Try all known ports
        for port in settings.POSSIBLE_PORTS:
            try:
                self.serial = Serial(port=port, baudrate=settings.BAUDRATE, timeout=3)
                self._logger.info(str.format("Using device in port: {}", port))
                break
            except SerialException:
                continue
        if not self.serial:
            self._logger.error('Device not found in any of the known ports')

    def set_up(self):
        self.get_status()
        self.get_relax_parameters()
        self.get_relax_data()
        self.reset_relax_variables()
        self.turn_spi_on()
        self.request_5_packets(0)
        self.turn_spi_off()
        self.request_5_packets(0)
        self.set_rf_mode()
        self.request_5_packets(0)
        self.turn_module_on()
        self.turn_uc_on()

    def request_data(self):
        packet = self.basic_request(0x10, payload=[0x00],
                                    msg='Request wireless truesense data from unicon')
        return WirelessDataPacket(packet.payload, scale=self.scale)

    def get_status(self):
        return self.basic_request(0x10, payload=[0x01], msg='Gets the plugged in UC status')

    def get_measure(self):
        return self.basic_request(0x10, payload=[0x10],
                                  msg='Request wireless measurement of current channel from slave')

    def get_relax_data(self):
        return self.basic_request(0x14, payload=[0x00], msg='Get the relax state data')

    def reset_relax_variables(self):
        return self.basic_request(0x14, payload=[0x02],
                                  msg='Reset the variables related to relax state in controller')

    def get_relax_parameters(self):
        return self.basic_request(0x14, payload=[0x04],
                                  msg='Get the parameters used in calculating the Relax state')

    def set_rf_mode(self):
        return self.basic_request(0x20, payload=[0x04], msg='Sets the plugged in truesense RF Mode')

    def turn_spi_on(self):
        return self.basic_request(0x20, payload=[0x0B],
                                  msg='Turn controller microSD SPI interface on')

    def turn_module_on(self):
        return self.basic_request(0x20, payload=[0x21],
                                  msg='Turn module on through unified controller')  #

    def turn_uc_on(self):
        return self.basic_request(0x20, payload=[0x23],
                                  msg='Set controller to on-state where it will turn on')

    def turn_spi_off(self):
        return self.basic_request(0x20, payload=[0x24],
                                  msg='Turn controller microSD SPI interface off')

    def request_5_packets(self, from_idx=0):
        return self.basic_request(0x2A,
                                  payload=[0x00, (from_idx >> 16) & 0xFF, (from_idx >> 8) & 0xFF, from_idx & 0xFF],
                                  msg='Request for 5 packets of interpreted data from memory module')

    def basic_request(self, data_code, payload=None, msg='About to send a packet to the device'):
        """
        This method sends a generic packet to the device
        This packet is defined by the Link protocol and the Wired frame

            @params:
                * data_code: data code defined int the Wired Frame definition
                * payload [List]: also defined in the Wired Frame definition, contains sud_data_code
        """
        self._logger.debug(msg)

        wired = WiredPacket(data_code, payload or [])
        packet = LinkPacket(payload=wired.to_list())

        self._write_packet(packet.to_list())
        return self._read_packet()

    def _write_packet(self, packet):
        self._logger.debug(str.format('About to write a packet: {}', packet))
        self.serial.write(packet)

    def _read_packet(self, src=None):
        if src is None:
            src = self.serial
        return LinkPacket.read_from_stream(src, self._logger)

    def save_values_to_file(self, path=settings.TEMP_SCAN, data=None):
        with open(path, 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)

    def sample_size(self, size=1):
        adc_values = []
        temperatures = []
        x_values = []
        y_values = []
        z_values = []

        while len(adc_values) < size:
            packet = self.request_data()
            if packet.has_data():
                adc_values = adc_values + packet.adc_values
                temperatures.append(packet.temperature)
                x_values.append(packet.accelerometer[0])
                y_values.append(packet.accelerometer[1])
                z_values.append(packet.accelerometer[2])

        return self.build_data_json(adc_values, temperatures, x_values, y_values, z_values)

    def build_data_json(self, adc=None, temperatures=None, x=None, y=None, z=None):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

        data = {
            'type': 'TrueSense',
            'timestamp': st
        }

        if adc is not None:
            data['adc_values'] = adc
        if temperatures is not None:
            data['temperatures'] = temperatures
        if x is not None:
            data['x'] = x
        if y is not None:
            data['y'] = y
        if z is not None:
            data['z'] = z
        return data


def grouped(iterable, n):
    return zip(*[iter(iterable)] * n)


def number_to_2s_complement(number, n):
    return number if (number >> n - 1) == 0 else number - (1 << n)


def byte_to_string(number):
    return '{0:08b}'.format(number)


alternate = lambda x: '0' if (x == '1') else '1'


def twos_complement_string_to_int(number):
    if number[0] == '1':
        l = list(map(alternate, list(number)))
        return -1 * (int(''.join(l), 2) + 1)
    else:
        return int(number, 2)


class LinkPacket():
    SYNC_BYTE = 0x33

    def __init__(self, header=None, payload=None, payload_length=0, checksum=0):
        self.header = header or []
        self.payload = payload or []
        self.checksum = checksum
        self.payload_length = payload_length

    def to_list(self):
        sync = LinkPacket.SYNC_BYTE
        return [sync, sync] + self._get_length() + self.payload + self._get_checksum()

    @classmethod
    def read_from_stream(cls, stream, logger):
        logger.debug('About to read a link packet...')
        header = stream.read(4)
        if header[0] != cls.SYNC_BYTE or header[1] != cls.SYNC_BYTE:
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

        return LinkPacket(header=list(header), payload=payload, payload_length=payload_length,
                          checksum=checksum)

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
    def __init__(self, data_code, payload=None):
        self.data_code = data_code
        self.payload = payload or []

    def to_list(self):
        return [self.data_code] + self.payload


# This class represents data defined in the Wired Frame Definition as:
#
# - Interpreted/Fixed Received Wireless TrueSense Data
class WirelessDataPacket():
    # Values used for scale
    VALUE_MAX = 32767  # max number to read
    VALUE_MIN = -32768  # min number to read
    VALUE_RANGE = VALUE_MAX - VALUE_MIN
    PHYSICAL_MAX = 800  # max physical measure [uV]
    PHYSICAL_MIN = -800  # min physical measure [uV]
    PHYSICAL_RANGE = PHYSICAL_MAX - PHYSICAL_MIN
    # Constants
    HAS_DATA = 0x01
    NO_DATA = 0x40
    VALID_DATA_CODE = 0x01
    SAMPLE_QUALITY_MASK = 0x03
    CORRUPTED_DATA = 3
    ED_MASK = 0x7F
    ADC_VALUE_LENGTH = 14
    BYTE_VALUE_LENGTH = 8

    def __init__(self, payload, scale=True):
        self.payload = payload
        self.scale = scale
        self._logger = get_logger()

        self.adc_values = []
        self.data_code = 0
        self.sub_data_code = 0
        self.timestamp = 0
        self.paired_device_number = 0
        self.miscellaneous_data = 0
        self.battery = 0
        self.temperature = 0
        self.accelerometer = (0, 0, 0)
        self.ed_measurement = 0

        self._analyze()

    @classmethod
    def max_value(cls, scale):
        return cls.PHYSICAL_MAX if scale else cls.VALUE_MAX

    @classmethod
    def min_value(cls, scale):
        return cls.PHYSICAL_MIN if scale else cls.VALUE_MIN

    def battery_status(self):
        if self.battery == 1:
            self._logger.info('Battery level above 3.15V')
            return True

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

        # Check data corruption
        data_corruption = adc_channel[1] & WirelessDataPacket.SAMPLE_QUALITY_MASK
        if data_corruption == WirelessDataPacket.CORRUPTED_DATA:
            self._logger.debug('Corrupted data found')
            return

        for high, low in grouped(adc_channel, 2):
            h_s = byte_to_string(high)
            l_s = byte_to_string(low)
            t_s = h_s + l_s[0:6]
            # number = number_to_2s_complement((high << 6) + (low >> 2), WirelessDataPacket.ADC_VALUE_LENGTH)
            number = twos_complement_string_to_int(t_s)
            number = self._scale(number)
            self.adc_values.append(number)

    def _decode_temperature(self):
        temp_code = self.payload[-8]
        self.temperature = (temp_code * 1.13) - 46.8

    def _decode_accelerometer(self):
        raw_data = self.payload[-7:-1]
        # accelerometer_x = number_to_2s_complement(raw_data[0], WirelessDataPacket.BYTE_VALUE_LENGTH)
        # accelerometer_y = number_to_2s_complement(raw_data[1], WirelessDataPacket.BYTE_VALUE_LENGTH)
        accelerometer_x = twos_complement_string_to_int(byte_to_string(raw_data[0]))
        accelerometer_y = twos_complement_string_to_int(byte_to_string(raw_data[2]))
        # Z values are sampled at a higher rate, thus giving 4 values
        z = [
            twos_complement_string_to_int(byte_to_string(raw_data[2])),
            twos_complement_string_to_int(byte_to_string(raw_data[3])),
            twos_complement_string_to_int(byte_to_string(raw_data[4])),
            twos_complement_string_to_int(byte_to_string(raw_data[5]))
            # number_to_2s_complement(raw_data[2], WirelessDataPacket.BYTE_VALUE_LENGTH),
            # number_to_2s_complement(raw_data[3], WirelessDataPacket.BYTE_VALUE_LENGTH),
            # number_to_2s_complement(raw_data[4], WirelessDataPacket.BYTE_VALUE_LENGTH),
            # number_to_2s_complement(raw_data[5], WirelessDataPacket.BYTE_VALUE_LENGTH)
        ]
        accelerometer_z = statistics.mean(z)

        self.accelerometer = (accelerometer_x, accelerometer_y, accelerometer_z)

    def _decode_ed_measurement(self):
        self.ed_measurement = self.payload[-1] & WirelessDataPacket.ED_MASK

    def _scale(self, number):
        scaled = number
        if self.scale:
            scaled = (((number - WirelessDataPacket.VALUE_MIN) * WirelessDataPacket.PHYSICAL_RANGE) / WirelessDataPacket.VALUE_RANGE) + WirelessDataPacket.PHYSICAL_MIN
        return scaled


class FilePacket():
    def __init__(self, header=None, payload=None):
        self.header = header or []
        self.payload = payload or []

    @classmethod
    def read_from_stream(cls, stream, scale=False):
        # From OPIFileDefinition_v1.00_20130503.pdf
        header = stream.read(512)[0:127]
        payload = []

        while stream.has_next():
            wrapper = LinkPacket.read_from_stream(stream, get_logger())
            payload.append(WirelessDataPacket(wrapper.payload, scale))

        return FilePacket(header, payload)


class SyncError(Exception):
    def __init__(self, message='SYNC bytes do not match'):
        super(SyncError, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class SizeDoesNotMatchError(Exception):
    def __init__(self, message):
        super(SizeDoesNotMatchError, self).__init__(message)
        self.message = message

    def __str__(self):
        return format("Size of %s does not match", self.message)


class ChecksumError(Exception):
    def __init__(self, message='Checksum does not validate data'):
        super(ChecksumError, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)


class DataCodeError(Exception):
    def __init__(self, expected, got):
        self.expected = expected
        self.got = got

    def __str__(self):
        return repr(
            str.format('Invalid data code. Expected {} but received {}', self.expected, self.got))

class TrueSenseDataPacket(DataPacket):
    def __init__(self, packet):
        self.packet = packet

    def get_channels(self):
        return [[self.packet.adc_values] + self.packet.accelerometer]

    def has_data(self):
        return self.packet.has_data()

class TrueSenseController(EMGController):
    def __init__(self):
        super(TrueSenseController, self).__init__()
        self.controller = Controller()
        self.controller.set_up()
        self.n_channels = 4
    
    def read_data(self):
        return TrueSenseDataPacket(self.controller.request_data())

    def build_json_data(self, channels):
        self.controller.build_data_json(adc=channels[0], x=channels[1], y=channels[2], z=channels[3])