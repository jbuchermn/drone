from abc import abstractmethod

from .camera import Camera
from ..util import Bitrate, WSBroadcast, NonBlockingFile


_sep = {
    'h264': b'\x00\x00\x00\x01',
    'mjpeg': b'\xFF\xD8'
}


class PythonSpaceCamera(Camera):
    def __init__(self, gallery, ws_port):
        super().__init__(gallery, ws_port)
        self._ws_broadcast = WSBroadcast('Camera', self.ws_port)
        self._bitrate = Bitrate('Camera')

        self._dat = bytearray()  # Used in _on_buffer mode
        self._cur_file = None

        self._ws_broadcast.start()

    def _on_buffer(self, buf):
        """
        Deliver a buffer, not necessarily a whole frame
        buf: bytes-object, the buffer

        To be called by the subclasses implementing backends
        """

        sep = _sep[self.get_current_config().format]
        self._dat += buf
        i = self._dat.find(sep, len(sep))
        while i != -1:
            frame = self._dat[0:i]
            self._dat = self._dat[i:]
            self._on_frame(frame)
            i = self._dat.find(sep, i + len(sep))

    def _on_frame(self, frame):
        """
        Deliver a whole frame

        To be called by the subclasses implementing backends
        or by _on_buffer
        """
        self._bitrate.register(len(frame))
        self._ws_broadcast.message(frame)
        if self._cur_file is not None:
            self._cur_file.write(frame)

    @abstractmethod
    def _py_image(self, config, path):
        """
        Same as _image
        """
        pass

    @abstractmethod
    def _py_start(self, config):
        """
        Start capturing stream calling either _on_frame or _on_buffer
        """
        pass

    @abstractmethod
    def _py_stop(self):
        """
        Stop capturing
        """
        pass

    @abstractmethod
    def _py_close(self):
        """
        Same as _close
        """
        pass

    """
    Camera API
    """
    def _image(self, config, path):
        self._py_image(config, path)

    def _start(self, mode, config, path=None):
        if path is not None:
            self._cur_file = NonBlockingFile(path, 'wb')
            self._cur_file.start()

        self._py_start(config)

    def _stop(self):
        self._py_stop()

        if self._cur_file is not None:
            self._cur_file.close()
            self._cur_file = None

    def _close(self):
        self._ws_broadcast.stop()
        if self._cur_file is not None:
            self._cur_file.close()

        self._py_close()
