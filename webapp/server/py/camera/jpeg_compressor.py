from threading import Thread
from queue import Queue
from .jpeg_reencode.build.jpeg_reencode import reencode
import time


class _Worker(Thread):
    def __init__(self, parent, num, quality):
        super().__init__()
        self._parent = parent
        self._quality = quality
        self._num = num
        self._running = True
        self._queue = Queue()

    def put(self, frame):
        self._queue.put(frame)

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            try:
                frame = self._queue.get(True, 1)
                print("S(%d): %d" % (self._num, id(frame)))
                nframe = reencode(frame, 100./self._quality)
                print("D(%d): %d" % (self._num, id(frame)))
                self._parent.deliver_frame(nframe)
            except Exception as err:
                print(err)
                pass



class JPEGCompressor:
    def __init__(self, on_frame, n_threads, quality):
        self._on_frame = on_frame
        self._threads = [_Worker(self, i, quality) for i in range(n_threads)]
        for t in self._threads:
            t.start()

        self._current = 0

    def close(self):
        for t in self._threads:
            t.stop()

    def deliver_frame(self, frame):
        self._on_frame(frame)

    def on_frame(self, frame):
        self._threads[self._current].put(frame)
        self._current = (self._current + 1) % len(self._threads)

