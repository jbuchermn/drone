import time

_streams = {}

class Stream:
    def __init__(self, name, keep=600):
        self.name = name
        self.keep = keep
        self.t = []
        self.val = []

        _streams[self.name] = self

    def register(self, val):
        self.t += [time.time()]
        self.val += [val]

    def clean(self):
        while len(self.t) > 0 and self.t[0] < time.time() - self.keep:
            del self.t[0]
            del self.val[0]

def get_streams():
    for k in _streams:
        _streams[k].clean()
    return {k:_streams[k] for k in _streams if len(_streams[k].t)>0}
