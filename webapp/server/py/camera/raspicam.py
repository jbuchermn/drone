import picamera
import traceback
import os

from ..util.ws_broadcast import WSBroadcast
from ..util.non_blocking_file import NonBlockingFile
from ..util.bitrate import Bitrate

SEP = {
    'h264': b'\x00\x00\x00\x01',
    'mjpeg': b'\xFF\xD8'
}

PROPS = [
    "framerate",
    "resolution",
    "vflip",
    "hflip"
]

DEFAULT_VIDEO = {
    'vflip': True,
    'hflip': True,
    'resolution': (640, 480),
    'framerate': 30,
    'format': 'mjpeg',
    'bitrate': 5000000
}

DEFAULT_IMAGE = {
    'vflip': True,
    'hflip': True,
    'quality': 100,
    'resolution': (2592, 1944),
}


def _patch_with_default(options, defaults):
    for d in defaults:
        options[d] = options.get(d, defaults[d])


class RaspiCam:
    def __init__(self, gallery, ws_port=None):
        self.gallery = gallery

        self._camera = picamera.PiCamera()
        self._on_frame_handlers = []
        self._dat = bytearray()

        self._current_video_config = None
        self._current_video_mode = None
        self._current_video_file = None
        self._current_video_entry = None

        self._bitrate = Bitrate('raspicam')

        self._ws_broadcast = WSBroadcast('raspicam', ws_port if ws_port is not None else 8088)
        self._ws_broadcast.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self.stop()
        self._camera.close()
        self._ws_broadcast.stop()

        if self._current_video_file is not None:
            self._current_video_file.close()

    def is_recording(self):
        """
        Whether recording to file is taking place
        """
        return self._current_video_mode == 'both' or \
            self._current_video_mode == 'file'

    def current_config(self):
        if self._current_video_config is None:
            return None
        else:
            return dict(self._current_video_config)

    def write(self, b):
        if self._current_video_config is None:
            return

        self._bitrate.register(len(b))

        """
        Handle file
        """
        if self.is_recording():
            self._current_video_file.write(b)

        """
        Handle frames in modes 'stream' and 'both'
        """
        sep = SEP[self._current_video_config['format']]

        self._dat += b
        i = self._dat.find(sep, len(sep))
        while i != -1:
            frame = self._dat[0:i]
            self._dat = self._dat[i:]
            self._ws_broadcast.message(frame)
            i = self._dat.find(sep, i + len(sep))

    def _handle_options(self, options):
        options_at_call = {v: options[v] for v in options if v not in PROPS}
        options_at_object = {v: options[v] for v in options if v in PROPS}

        for v in options_at_object:
            prop = getattr(type(self._camera), v)
            if prop.fget(self._camera) != options_at_object[v]:
                prop.fset(self._camera, options_at_object[v])

        return options_at_call

    def start(self, mode='stream', **kwargs):
        """
        Start recording and return

        mode is
            'stream': Only pass frames to on_frame_listeners
            'both': Pass frames to on_frame_listeners and save to path
                (saving will not be restarted after image)
            'file': Only save to path (will not be restarted after image)
        """
        self.stop()

        options = dict(kwargs)
        _patch_with_default(options, DEFAULT_VIDEO)

        """
        Store
        """
        path = None
        if mode == 'both' or mode == 'file':
            self._current_video_entry = self.gallery.new_video(format=options['format'])
            self._current_video_file = NonBlockingFile(self._current_video_entry.filename(), 'wb')
            self._current_video_file.start()

        self._current_video_config = options
        self._current_video_mode = mode

        options_at_call = self._handle_options(options)
        stream = path if mode == 'file' else self
        self._camera.start_recording(stream, **options_at_call)

    def stop(self):
        """
        Stop stream cleaning up
        """
        try:
            self._camera.stop_recording()  # Throws PiCameraNotRecording
        except Exception:
            pass
        self._current_video_config = None
        self._current_video_mode = None
        if self._current_video_file is not None:
            self._current_video_file.close()
            self._current_video_file = None

        if self._current_video_entry is not None:
            self._current_video_entry.process()
            self._current_video_path = None

    def image(self, **kwargs):
        """
        Synchronously take image
        """
        resume_config = self._current_video_config
        resume_mode = self._current_video_mode

        if resume_mode == 'file':
            resume_config = None
            resume_mode = None
        elif resume_mode == 'both':
            resume_mode = 'stream'

        self.stop()

        options = dict(kwargs)
        _patch_with_default(options, DEFAULT_IMAGE)

        options_at_call = self._handle_options(options)

        entry = self.gallery.new_image(format='jpg')
        self._camera.capture(entry.filename(), **options_at_call)
        entry.process()

        if resume_mode is not None and resume_config is not None:
            self.start(mode=resume_mode, **resume_config)

    def get_ws_port(self):
        return self._ws_broadcast.port

