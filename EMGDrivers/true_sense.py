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

    def get_status(self):
        packet = Packet.create_packet(REQUEST_STATUS_DATA_CODES[0], [REQUEST_STATUS_DATA_CODES[1]])
        self._write_packet(packet)
        return self._read_packet()

    def _write_packet(self, packet):
        self._logger.info(str.format('About to write a packet: {}', packet))
        self.serial.write(packet)

    def _read_packet(self):
        self._logger.info('About to read a packet...')
        header = self.serial.read(4)
        if header[0] != SYNC_BYTE or header[1] != SYNC_BYTE:
            self._logger.debug('Sync bytes were:')
            self._logger.debug(header[0])
            self._logger.debug(header[1])
            raise SyncError

        payload_length = (header[2] << 8) + header[3]
        payload = list(self.serial.read(payload_length))
        if payload_length != len(payload):
            self._logger.debug('Payloads lengths were:')
            self._logger.debug(payload_length)
            self._logger.debug(len(payload))
            raise SizeDoesNotMatchError('payload')

        checksum = self.serial.read(2)
        checksum = (checksum[0] << 8) + checksum[1]
        if sum(payload) != checksum:
            self._logger.debug('Payload was:')
            self._logger.debug(payload)
            self._logger.debug(format('Calculated checksum was: %d', sum(payload)))
            self._logger.debug(format('Provided checksum was: %d', checksum))
            raise ChecksumError

        return (list(header), payload, checksum)


class Packet:
    def create_packet(data_code, payload):
        wired = Packet._wired_packet(data_code, payload)
        return Packet._link_packet(wired)

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
