import queue
import threading

import emg_shield
from logger import get_logger
import plotters
import settings

logger = get_logger()
plotter = plotters.mpl.DynamicPlotter(x_range=5000,min_val=0,max_val=2000, linewidth=1.0)
c = emg_shield.Controller()
q = queue.Queue()

class ReaderThread(threading.Thread):
    def __init__(self):
        self._end = False
        super(ReaderThread, self).__init__()

    def run(self):
        for p in c.read_data(50000):
            q.put(p.channels)
        q.put(None)

    def stop(self):
        self._end = True

# reader = ReaderThread()
# reader.start()


try:
    for p in c.read_data(200000):
        # logger.info(q.qsize())
        vals = p.channels  
        if vals is None:
            exit(1)
        plotter.plotdata(vals)
except Exception as e:
    logger.exception(e)
    pass
finally:
    c.close()



