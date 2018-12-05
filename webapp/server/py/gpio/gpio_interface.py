import time
from threading import Thread
from .simple_interface import SimpleInterface, LEDState
from ..camera import StreamingMode
from ..util import get_network_state, NetworkState
from ..server import auto_hotspot

class GPIOInterface(Thread):
    def __init__(self, server):
        super().__init__()
        self._server = server
        self._interface = SimpleInterface()
        self._interface.set_led(0, LEDState(on=True, blink_interval=5))
        self._interface.on_switch(0, self.toggle_hotspot)
        self._interface.on_switch(1, self.record)

        self._running = True
        self.start()

        self._network_state = None
        self._Streaming_mode = None


    def toggle_hotspot(self):
        if self._network_state == NetworkState.CLIENT:
            self._server.auto_hotspot(force=True)
        else:
            self._server.auto_hotspot(force=False)

    def record(self):
        if self._streaming_mode == StreamingMode.FILE or self._streaming_mode == StreamingMode.BOTH:
            self._server.cam.stop()
        else:
            self._server.cam.start(StreamingMode.FILE)
            

    def run(self):
        while self._running:
            ns = get_network_state()
            sm = self._server.cam.get_current_streaming_mode()

            if ns == NetworkState.HOTSPOT:
                self._interface.set_led(1, LEDState(on=True))
            elif ns == NetworkState.CLIENT:
                self._interface.set_led(1, LEDState(on=False))
            else:
                self._interface.set_led(1, LEDState(on=True, blink_interval=1))

            if sm == StreamingMode.FILE or sm == StreamingMode.BOTH:
                self._interface.set_led(2, LEDState(on=True, blink_interval=5))
            elif sm == StreamingMode.STREAM:
                self._interface.set_led(2, LEDState(on=True))
            else:
                self._interface.set_led(2, LEDState(on=False))

            if self._server.mavlink_proxy.get_proxy() is not None:
                self._interface.set_led(3, LEDState(on=True))
            else:
                self._interface.set_led(3, LEDState(on=False))

            self._network_state = ns
            self._streaming_mode = sm

            time.sleep(1.)


    def close(self):
        self._running = False
        self._interface.close()
