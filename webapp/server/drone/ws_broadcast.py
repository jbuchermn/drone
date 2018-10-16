from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Thread


class WSBroadcast(Thread):
    def __init__(self, name, port):
        super().__init__()
        self.name = name
        self.port = port
        self.stopped = False
        self._server = SimpleWebSocketServer('', self.port, WebSocket)

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
                self._server.connections[c].sendMessage(msg)

