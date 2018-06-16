from queue.queue import Queue
import os

if __name__ == '__main__':
    q = Queue()
    q.publish_event({'uuid': '123-test', 'signal': [123, 234, 345]})
    #import socket
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect(("8.8.8.8", 80))
    #q.publish_state({'IP': s.getsockname()[0]})
    #s.close()

