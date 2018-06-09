import threading

class DataCollectionThread(threading.Thread):
    def __init__(self, controller, storage):
        super(DataCollectionThread, self).__init__()
        self.controller = controller
        self.get_values = True
        self.storage = storage

    def run(self):
        while self.get_values:
            packet = self.controller.read_data()
            if packet.has_data():
                self.storage.extend(packet.get_channels()[0]) # We only care for channel0

    def stop(self):
        self.get_values = False
