class EMGController(object):
    def __init__(self):
        self.n_channels = 0

    def read_data(self):
        raise NotImplementedError

    def build_json_data(self, channels):
        return NotImplementedError
    
class DataPacket(object):
    def get_channels(self):
        raise NotImplementedError
    
    def has_data(self):
        raise NotImplementedError

