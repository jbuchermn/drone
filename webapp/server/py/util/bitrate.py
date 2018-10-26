import time
from .stream import Stream


class Bitrate:
    def __init__(self, name):
        self._name = name
        self._t = []  # seconds
        self._b = []  # bytes
        self._stream = Stream(self._name + " (Mbit/s)")

    def register(self, db):
        self._t += [time.time()]
        self._b += [db]

        if self._t[-1] - self._t[0] > 1.:
            n_bytes = sum(self._b[:-1])
            delta_t = self._t[-2] - self._t[0]
            self._stream.register(8*n_bytes/delta_t/1e6)
            self._t = self._t[-1:]
            self._b = self._b[-1:]

