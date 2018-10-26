import traceback
from abc import abstractmethod
from enum import Enum


class StreamingMode(Enum):
    """
    Stream to websocket
    """
    STREAM = 1,

    """
    Save to file
    """
    FILE = 2,

    """
    Save while streaming to websocket
    """
    BOTH = 3


class CameraConfig:
    def __init__(self, format=None, **kwargs):
        if format is None:
            raise Exception("Need to specify format")

        self.format = format
        self.options = kwargs

    def get_dict(self):
        return {
            'format': self.format,
            **self.options
        }

    def set(self, key, val):
        if key == 'format':
            self.format = val
        else:
            self.options[key] = val


class Camera:
    """
    Abstract base class providing functionality:
        * Capture an image to a file
        * Capture a video to a file
        * Stream a video to a websocket
        * Stream a video to a websocket and store it
            to a file during the broadcast
    """

    def __init__(self, gallery, ws_port):
        self.gallery = gallery
        self.ws_port = ws_port

        """
        Set during streaming
        """
        self._cur_config = None
        self._cur_mode = None

        """
        Set during streaming if mode == FILE or mode == BOTH
        """
        self._cur_entry = None

    @abstractmethod
    def _image(self, config, path):
        """
        Take an image (synchronously)

        config: Instance of CameraConfig
        path: Where to store the image

        _stop is guaranteed to be called beforehand if streaming/saving
        was in progress
        """
        pass

    @abstractmethod
    def _start(self, mode, config, path=None):
        """
        Start streaming/capturing

        mode: Instance of StreamingMode
        config: Instance of CameraConfig
        path: where to store if mode == FILE or mode == BOTH

        This method should alter the CameraConfig instance
        to inform the caller about defaults or unsupported
        configuration

        _stop is guaranteed to be called beforehand if streaming/saving
        was in progress
        """
        pass

    @abstractmethod
    def _stop(self):
        """
        Stop any streaming/capturing
        """
        pass

    @abstractmethod
    def _close(self):
        """
        Free all resources
        """
        pass

    """
    Public API
    """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self._close()

    def image(self, config):
        if self._cur_config is not None:
            self.stop()

        entry = self.gallery.new_image(config.format)
        self._image(config, entry.filename())
        entry.process()

    def start(self, mode, config):
        if self._cur_config is not None:
            self.stop()

        self._cur_mode = mode
        self._cur_config = config

        path = None
        if mode == StreamingMode.FILE or mode == StreamingMode.BOTH:
            self._cur_entry = self.gallery.new_video(format=config.format)
            path = self._cur_entry.filename()

        self._start(mode, self._cur_config, path=path)

    def stop(self):
        self._stop()
        if self._cur_entry is not None:
            self._cur_entry.process()
            self._cur_entry = None
        self._cur_mode = None
        self._cur_config = None

    def get_current_streaming_mode(self):
        return self._cur_mode

    def get_current_config(self):
        return self._cur_config
