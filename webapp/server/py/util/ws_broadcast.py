from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread
from queue import Queue

from .rate_stream import RateStream


class _Dispatcher(Thread):
    def __init__(self, broadcast):
        super().__init__()
        self._broadcast = broadcast
        self._queue = Queue()
        self._running = True

    def run(self):
        while self._running:
            try:
                msg = self._queue.get(True, 1)
                self._broadcast.sync_message(msg)
            except Exception:
                pass

    def message(self, msg):
        self._queue.put(msg)

    def close(self):
        self._running = False

class WSBroadcast(Thread):
    def __init__(self, name, port):
        super().__init__()
        self.name = name
        self.port = port
        self._running = True
        self._dispatcher = _Dispatcher(self)
        self._server = SimpleWebSocketServer('', self.port, WebSocket)
        self._bitrates = {}

    def close(self):
        self._running = False
        self._dispatcher.close()

    def run(self):
        self._dispatcher.start()
        print("Opening WS broadcast '%s' on port %d..." %
              (self.name, self.port))
        while self._running:
            self._server.serveonce()

    def message(self, msg):
        self._dispatcher.message(msg)

    def sync_message(self, msg):
        for c in self._server.connections:
            """
            Just skip the message if send is in progress
            """
            if len(self._server.connections[c].sendq) <= 1:
                if c not in self._bitrates:
                    self._bitrates[c] = RateStream('Websocket: %s (Mbit/s)' % c)

                self._bitrates[c].register(len(msg)*8./1.e6)
                self._server.connections[c].sendMessage(msg)

