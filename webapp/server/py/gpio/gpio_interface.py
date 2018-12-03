from .simple_interface import SimpleInterface

class GPIOInterface:
    def __init__(self, server):
        self._server = server
        self._interface = SimpleInterface()
        self._interface.set_led(0, 1)

    def close(self):
        self._interface.close()
