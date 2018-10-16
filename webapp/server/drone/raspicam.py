import picamera
import traceback
import os

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
    'resolution': (1280, 720),
    'framerate': 30,
    'format': 'mjpeg',
    'quality': 50,
    'bitrate': 100000000
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
    def __init__(self, gallery):
        self.gallery = gallery

        self._camera = picamera.PiCamera()
        self._on_frame_handlers = []
        self._dat = bytearray()

        self._current_video_config = None
        self._current_video_mode = None
        self._current_video_path = None
        self._current_video_file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self.stop()
        self._camera.close()

    def on_frame(self, handler):
        self._on_frame_handlers += [handler]

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
        """
        Called during recording by the camera in modes 'stream' and 'both'
        """
        if self._current_video_config is None:
            return

        """
        Handle file in mode 'both'
        """
        if self._current_video_file is not None:
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
            for f in self._on_frame_handlers:
                f(frame)
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
            path = self.gallery.new_video(format=options['format'])

            """
            Change to .filename during recording
            """
            path = os.path.join(
                os.path.dirname(path),
                '.' + os.path.basename(path)
            )
            self._current_video_path = path
        else:
            self._current_video_path = None

        self._current_video_config = options
        self._current_video_mode = mode
        if mode == 'both':
            self._current_video_file = open(path, 'wb')

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

        """
        Videos are stored as .filename at first and after recording
        is finished moved to filename
        """
        if self._current_video_path is not None:
            path = os.path.join(
                os.path.dirname(self._current_video_path),
                os.path.basename(self._current_video_path)[1:]
            )

            os.rename(self._current_video_path, path)
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

        path = self.gallery.new_image(format='jpg')
        self._camera.capture(path, **options_at_call)

        if resume_mode is not None and resume_config is not None:
            self.start(mode=resume_mode, **resume_config)


if __name__ == '__main__':
    import time

    with RaspiCam() as cam:
        """
        Test 1: Take a JPEG
        """
        print("Taking picture...")
        cam.image("test1.jpg")

        """
        Test 2: Record MJPEG directly to file
        """
        print("Starting mode == 'file'...")
        cam.start(mode='file', path='test2.mjpeg',
                  format='mjpeg',
                  quality=90,
                  resolution=(1920, 1080),
                  framerate=30,
                  bitrate=100000000)
        time.sleep(5)
        print("Is recording? %s" % cam.is_recording())
        cam.stop()
        print("...done")
        print("Is recording? %s" % cam.is_recording())

        """
        Test 3: Stream MJPEG and save it simultaneously
        """
        with open('test3_2.mjpeg', 'wb') as outf:
            def write(frame):
                outf.write(frame)
            cam.on_frame(write)
            print("Starting mode == 'both'...")
            cam.start(mode='both', path='test3.mjpeg',
                      format='mjpeg',
                      quality=20,
                      resolution=(1280, 720),
                      framerate=30,
                      bitrate=10000000)
            time.sleep(5)
            print("Is recording? %s" % cam.is_recording())
            print("Interrupting with picture...")
            cam.image("test4.jpg")
            print("Is recording? %s" % cam.is_recording())
            time.sleep(5)
            cam.stop()
            print("...done")
            print("Is recording? %s" % cam.is_recording())

