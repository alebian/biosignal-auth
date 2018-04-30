import threading
class DataCollectionThread(threading.Thread):
    def __init__(self, controller, subject_name, sample_n):
        super(DataCollectionThread, self).__init__()
        self.controller = controller
        self.channels = [[] for n in range(0,self.controller.n_channels)]
        self.get_values = True
        self.subject_name = subject_name
        self.sample_n = sample_n

    def run(self):
        while self.get_values:
            packet = self.controller.read_data()
            if packet.has_data():
                for i, channel in enumerate(packet.get_channels()):
                    self.channels[i] += channel
        self.store_sample()

    def stop(self):
        self.get_values = False

    def store_sample(self):
        raise NotImplementedError()