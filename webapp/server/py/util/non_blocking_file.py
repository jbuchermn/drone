from threading import Thread
from queue import Queue
from .bitrate import Bitrate

class NonBlockingFile(Thread):
    def __init__(self, filename, mode):
        super().__init__()
        self._file = open(filename, mode)
        self._bitrate = Bitrate('file: %s' % filename)
        self._running = True
        self._queue = Queue()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self._file.close()
        self._running = False

    def write(self, data):
        self._queue.put(data)

    def run(self):
        while self._running:
            data = self._queue.get()
            self._file.write(data)
            self._bitrate.register(len(data))

