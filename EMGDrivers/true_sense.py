from serial import Serial, SerialException
from logger import get_logger

import settings

SYNC_BYTE = 0x33

# Tuples representing DataCode and SubDataCode
REQUEST_STATUS_DATA_CODES = (0x10, 0x01)


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

    def basic_request(self, data_code, sub_data_code):
        packet = Packet.create_packet(data_code, [sub_data_code])
        self._write_packet(packet)
        return self._read_packet()

    def get_status(self):
        packet = Packet.create_packet(REQUEST_STATUS_DATA_CODES[0], [REQUEST_STATUS_DATA_CODES[1]])
        self._write_packet(packet)
        return self._read_packet()

    def get_measure(self):
        packet = Packet.create_packet(0x10, [0x10])
        self._write_packet(packet)
        return self._read_packet()

    def _write_packet(self, packet):
        self._logger.debug(str.format('About to write a packet: {}', packet))
        self.serial.write(packet)

    def _read_packet(self, src=None):
        if src == None:
            src = self.serial

        return Packet.read_from_stream(src, self._logger)


class Packet:
    def create_packet(data_code, payload):
        wired = Packet._wired_packet(data_code, payload)
        return Packet._link_packet(wired)

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

    def _link_packet(payload):
        return [SYNC_BYTE, SYNC_BYTE] + Packet._get_length(payload) + payload + Packet._get_checksum(payload)

    def _wired_packet(data_code, payload):
        return [data_code] + payload

    def _get_checksum(payload):
        chk = sum(payload)
        high_byte = chk >> 8
        low_byte = chk
        return [high_byte, low_byte]

    def _get_length(payload):
        high_byte = ((len(payload)) >> 8) & 0xff
        low_byte = (len(payload)) & 0xff
        return [high_byte, low_byte]


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
