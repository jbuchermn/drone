from threading import Thread
from queue import Queue, Empty
import time
from .jpeg_reencode.build.jpeg_reencode import reencode
from ..util import Stream


class _Worker(Thread):
    def __init__(self, parent, num, quality):
        super().__init__()
        self._parent = parent
        self._quality = quality
        self._num = num
        self._running = True

        self._queue = Queue()
        self.ready = True

    def put(self, frame):
        self._queue.put(frame)

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            self.ready = True
            try:
                frame = self._queue.get(True, 1)
                self.ready = False
                t = time.time()
                frame = reencode(frame, 100./self._quality)
                t = time.time() - t
                self._parent.stream.register(1000. * t)
                self._parent.deliver_frame(frame)
            except Empty:
                pass


class JPEGCompressor:
    def __init__(self, on_frame, n_threads, quality):
        self._on_frame = on_frame
        self._threads = [_Worker(self, i, quality) for i in range(n_threads)]
        for t in self._threads:
            t.start()

        self._current = 0

        self._first = True
        self.stream = Stream('JPEG compression (ms)')

    def close(self):
        for t in self._threads:
            t.stop()

    def deliver_frame(self, frame):
        self._on_frame(frame)

    def on_frame(self, frame):
        if not self._threads[self._current].ready:
            return
        self._threads[self._current].put(frame)
        self._current = (self._current + 1) % len(self._threads)

