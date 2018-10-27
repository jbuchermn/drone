from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread

from .bitrate import Bitrate


class WSBroadcast(Thread):
    def __init__(self, name, port):
        super().__init__()
        self.name = name
        self.port = port
        self.stopped = False
        self._server = SimpleWebSocketServer('', self.port, WebSocket)
        self._bitrates = {}

    def stop(self):
        self.stopped = True

    def run(self):
        print("Opening WS broadcast '%s' on port %d..." %
              (self.name, self.port))
        while not self.stopped:
            self._server.serveonce()

    def message(self, msg):
        for c in self._server.connections:
            if len(self._server.connections[c].sendq) <= 1:
                if c not in self._bitrates:
                    self._bitrates[c] = Bitrate('Websocket: %s' % c)

                self._bitrates[c].register(len(msg))
                self._server.connections[c].sendMessage(msg)

