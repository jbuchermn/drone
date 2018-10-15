import picamera
import traceback

SEP = {
    'h264': b'\x00\x00\x00\x01',
    'mjpeg': b'\xFF\xD8'
}


class RaspiCam:
    def __init__(self):
        self._camera = picamera.PiCamera()
        self._on_frame_handlers = []
        self._current_video_config = None

        self._dat = bytearray()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self._camera.close()

    def on_frame(self, handler):
        self._on_frame_handlers += [handler]

    def _on_frame(self, frame):
        """
        Possibly make this async in the future
        """
        for f in self._on_frame_handlers:
            f(frame)

    def write(self, b):
        """
        Called during recording by the camera
        """
        if self._current_video_config is None:
            return
        sep = SEP[self._current_video_config['format']]

        self._dat += b
        i = self._dat.find(sep, len(sep))
        while i != -1:
            frame = self._dat[0:i]
            self._dat = self._dat[i:]
            self._on_frame(frame)
            i = self._dat.find(sep, i + len(sep))

    def start(self, **kwargs):
        """
        Start recording and return
        """
        self.stop()

        options = dict(kwargs)
        options['format'] = options.get("format", "mjpeg")
        self._current_video_config = options

        resolution = options.get("resolution", (1280, 720))
        framerate = options.get("framerate", 30)
        options_stripped = {v: options[v] for v in options
                            if v not in ["resolution", "framerate"]}

        self._camera.resolution = resolution
        self._camera.framerate = framerate
        self._camera.start_recording(self, **options_stripped)

    def stop(self):
        try:
            self._camera.stop_recording()  # Throws PiCameraNotRecording
        except Exception:
            pass
        self._current_video_config = None

    def image(self, path, **kwargs):
        """
        Synchronously take image
        """
        resume = None
        if self._current_video_config is not None:
            resume = self._current_video_config
        self.stop()

        resolution = kwargs.get("resolution", (2592, 1944))
        options_stripped = {v: kwargs[v] for v in kwargs
                            if v not in ["resolution", "framerate"]}

        self._camera.resolution = resolution
        self._camera.capture(path, **options_stripped)

        if resume is not None:
            self.start(**resume)


if __name__ == '__main__':
    import time

    with RaspiCam() as cam:
        with open('tmp.mjpeg', 'wb') as outf:
            def write(frame):
                outf.write(frame)
            cam.on_frame(write)
            cam.start(format='mjpeg',
                      quality=90,
                      resolution=(1920, 1080),
                      framerate=30,
                      bitrate=100000000)

            time.sleep(5)
            cam.image('tmp.jpg')
            time.sleep(5)
            print("Done")

