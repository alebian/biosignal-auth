from queue.queue import Queue
import os

if __name__ == '__main__':
    q = Queue()
    q.publish_state({'test': 123})
