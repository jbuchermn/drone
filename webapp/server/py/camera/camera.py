import traceback
import json
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
        if 'load_json' in kwargs and 'default' in kwargs:
            try:
                with open(kwargs['load_json'], 'r') as f:
                    kwargs = json.loads(f.read())
            except Exception:
                traceback.print_exc()
                kwargs = kwargs['default']

            format = kwargs['format']
            del kwargs['format']

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

    def save_json(self, path):
        with open(path, 'w') as f:
            f.write(json.dumps({'format': self.format, **self.options}))


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
        Load (and save in case of defaults) configuration
        """
        self._stream_config = CameraConfig(load_json='./stream_config.json', default={
            'format': 'mjpeg',
            'framerate': 10,
            'resolution': [320, 240]
        })
        self._stream_config.save_json('./stream_config.json')
        self._video_config = CameraConfig(load_json='./video_config.json', default={
            'format': 'mjpeg',
            'framerate': 30,
            'resolution': [1280, 720]
        })
        self._video_config.save_json('./video_config.json')
        self._image_config = CameraConfig(load_json='./image_config.json', default={
            'format': 'jpeg',
            'resolution': [1920, 1080]
        })
        self._image_config.save_json('./image_config.json')

        """
        Set during streaming
        """
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

    def image(self):
        if self._cur_mode is not None:
            self.stop()
            self._cur_mode = None

        entry = self.gallery.new_image(self._image_config.format)
        self._image(self._image_config, entry.filename())
        entry.process()

    def start(self, mode):
        if self._cur_mode is not None:
            self.stop()

        self._cur_mode = mode

        path = None
        if mode == StreamingMode.FILE or mode == StreamingMode.BOTH:
            self._cur_entry = self.gallery.new_video(format=self._video_config.format)
            path = self._cur_entry.filename()

        self._start(mode, self._stream_config if mode == StreamingMode.STREAM else self._video_config, path=path)

    def stop(self):
        self._stop()
        if self._cur_entry is not None:
            self._cur_entry.process()
            self._cur_entry = None
        self._cur_mode = None

    def get_current_streaming_mode(self):
        return self._cur_mode

    def get_stream_config(self):
        return self._stream_config

    def get_video_config(self):
        return self._video_config

    def get_image_config(self):
        return self._image_config

    def set_stream_config(self, config):
        self._stream_config = config
        self._stream_config.save_json('./stream_config.json')

    def set_video_config(self, config):
        self._video_config = config
        self._video_config.save_json('./video_config.json')

    def set_image_config(self, config):
        self._image_config = config
        self._image_config.save_json('./image_config.json')
