import picamera

from .python_space_camera import PythonSpaceCamera


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


class RaspiCam(PythonSpaceCamera):
    def __init__(self, gallery, ws_port):
        super().__init__(gallery, ws_port)
        self._camera = picamera.PiCamera()

    def close(self):
        super().close()
        self._camera.close()

    def _handle_options(self, options):
        options_at_call = {v: options[v] for v in options if v not in PROPS}
        options_at_object = {v: options[v] for v in options if v in PROPS}

        for v in options_at_object:
            prop = getattr(type(self._camera), v)
            if prop.fget(self._camera) != options_at_object[v]:
                prop.fset(self._camera, options_at_object[v])

        return options_at_call

    def __start(self, config):
        _patch_with_default(config, DEFAULT_VIDEO)
        options_at_call = self._handle_options(config)

        class _:
            def __init__(self, parent):
                self.parent = parent

            def write(self, b):
                self.parent._on_buffer(b)
        self._camera.start_recording(_(self), **options_at_call)

    def __stop(self):
        try:
            self._camera.stop_recording()  # Throws PiCameraNotRecording
        except Exception:
            pass

    def __image(self, config, path):
        _patch_with_default(config, DEFAULT_IMAGE)

        options_at_call = self._handle_options(config)

        self._camera.capture(path, **options_at_call)

