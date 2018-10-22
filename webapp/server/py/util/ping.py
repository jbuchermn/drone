from threading import Thread
import traceback
from subprocess import Popen, PIPE

from .stream import Stream

class Ping(Thread):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        self._running = True
        self._stream = Stream('ping: %s (ms)' % self.ip)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self._running = False

    def run(self):
        while self._running:
            p = Popen(("ping %s -c 2" % self.ip).split(" "), stdout=PIPE)
            stdout = p.communicate()[0].decode('utf-8').strip()
            try:
                stdout = stdout.split("\n")[-1]
                stdout = stdout.split("=")[1]
                stdout = stdout.split("/")[2]  # 0: min, 1: avg, 2: max, 3: mdev
                self._stream.register(float(stdout))
            except Exception:
                self._stream.register(-1)

