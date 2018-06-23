from emg_driver.emg_shield import EMGShieldController
from emg_driver.data_collection import DataCollectionThread

class DataCollectionManager(object):
    def __init__(self):
        self.thread = None
        self.controller = EMGShieldController()
        self.current_token = None
    
    def start_collection(self, values, token):
        self.current_token = token
        self.thread = DataCollectionThread(self.controller, values)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_collection(self):
        if self.thread is None:
            return
        self.thread.stop()
        self.thread.join()
        self.thread = None
        token = self.current_token
        self.current_token = None
        return token