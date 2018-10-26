import traceback
from threading import Thread
from queue import Queue
from .bitrate import Bitrate


_open_files = []


class NonBlockingFile(Thread):
    def __init__(self, filename, mode):
        global _open_files

        super().__init__()
        self._file = open(filename, mode)
        self._bitrate = Bitrate('file: %s' % filename)
        self._running = True
        self._queue = Queue()

        _open_files += [self]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        global _open_files

        self._file.close()
        self._running = False
        _open_files.remove(self)

    def write(self, data):
        self._queue.put(data)

    def run(self):
        while self._running:
            data = self._queue.get()
            self._file.write(data)
            self._bitrate.register(len(data))


def is_file_write_in_progress():
    return len(_open_files) > 0

