import time

_streams = {}

class Stream:
    def __init__(self, name, keep=120):
        self.name = name
        self.keep = keep
        self.t = []
        self.val = []

        _streams[self.name] = self

    def register(self, val):
        self.t += [time.time()]
        self.val += [val]

        if len(self.t) > self.keep:
            self.t = self.t[-self.keep:]
            self.val = self.val[-self.keep:]

def get_streams():
    return _streams
