import picamera

from .python_space_camera import PythonSpaceCamera

"""
Supported configuration key-words
"""

_props = [
    "framerate",
    "resolution",
    "vflip",
    "hflip"
]

_prop_defaults = {
    "framerate": 10,
    "resolution": (640, 480),
    "vflip": True,
    "hflip": True
}

_kwargs = [
    "format",
    "framerate",
    "bitrate"
]


def _patch_with_default(options, defaults):
    for d in defaults:
        options[d] = options.get(d, defaults[d])


class RaspiCam(PythonSpaceCamera):
    def __init__(self, gallery, ws_port):
        super().__init__(gallery, ws_port)
        self._camera = picamera.PiCamera()

    def _handle_config(self, config):
        kw = config.get_dict()

        for v in _props:
            prop = getattr(type(self._camera), v)
            if v in kw:
                if prop.fget(self._camera) != kw[v]:
                    prop.fset(self._camera, kw[v])
            elif v in _prop_defaults:
                if prop.fget(self._camera) != _prop_defaults[v]:
                    prop.fset(self._camera, _prop_defaults[v])

            """
            Update config to let the caller know about defaults
            """
            config.set(v, prop.fget(self._camera))

        return {v: kw[v] for v in kw if v not in _props}

    def __start(self, config):
        class _:
            def __init__(self, parent):
                self.parent = parent

            def write(self, b):
                self.parent._on_buffer(b)

        kwargs = self._handle_config(config)
        self._camera.start_recording(_(self), **kwargs)

    def __stop(self):
        try:
            self._camera.stop_recording()  # Throws PiCameraNotRecording
        except Exception:
            pass

    def __image(self, config, path):
        kwargs = self._handle_config(config)
        self._camera.capture(path, **kwargs)

    def __close(self):
        self._camera.close()
