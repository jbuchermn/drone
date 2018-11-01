import time
from .stream import Stream


class RateStream:
    def __init__(self, name):
        self._name = name
        self._t = []  # seconds
        self._d = []  # bytes
        self._stream = Stream(self._name)

    def register(self, delta):
        self._t += [time.time()]
        self._d += [delta]

        if self._t[-1] - self._t[0] > 1.:
            total = sum(self._d[:-1])
            delta_t = self._t[-2] - self._t[0]
            if delta_t == 0:
                delta_t = 1
            self._stream.register(total/delta_t)
            self._t = self._t[-1:]
            self._d = self._d[-1:]

