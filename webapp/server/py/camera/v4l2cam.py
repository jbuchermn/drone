from fcntl import ioctl
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from io import BytesIO
import mmap
import time
import select

from ..util import Stream, RateStream

from .python_space_camera import PythonSpaceCamera
from .v4l2 import (
    v4l2_fourcc_to_str,
    v4l2_capability,
    v4l2_format,
    v4l2_streamparm,
    v4l2_requestbuffers,
    v4l2_buffer,
    v4l2_buf_type,
    v4l2_queryctrl,
    VIDIOC_QUERYCAP,
    VIDIOC_REQBUFS,
    VIDIOC_QUERYBUF,
    VIDIOC_STREAMON,
    VIDIOC_QBUF,
    VIDIOC_DQBUF,
    VIDIOC_STREAMOFF,
    VIDIOC_G_FMT,
    VIDIOC_S_FMT,
    VIDIOC_G_PARM,
    VIDIOC_S_PARM,
    VIDIOC_QUERYCTRL,
    V4L2_BUF_TYPE_VIDEO_CAPTURE,
    V4L2_MEMORY_MMAP,
    V4L2_CAP_TIMEPERFRAME,
    V4L2_PIX_FMT_MJPEG
)


def _ubyte_to_str(arr):
    return "".join([chr(c) for c in arr])


class _JPEGStripper:
    def __init__(self, on_frame):
        self._on_frame = on_frame

    def close(self):
        pass

    def on_frame(self, frame):
        length_upper = len(frame)
        length_lower = 0

        def is_zero(frame, idx):
            for i in range(idx - 1, idx + 1):
                if i < 0 or i >= len(frame):
                    continue
                if frame[i] != 0:
                    return False
            return True

        for _ in range(10):
            tmp = int((length_upper + length_lower)/2)
            if is_zero(frame, tmp):
                length_upper = tmp
            else:
                length_lower = tmp

        length = length_upper
        while frame[length - 1] == 0:
            length -= 1

        self._on_frame(frame[:min(length + 3, len(frame))])



class _Stream(Thread):
    def __init__(self, fd, config, on_frame, num_buffers=2):
        super().__init__()
        self._fd = fd
        self._on_frame = on_frame
        self._running = True

        self._raw_fps = RateStream('Camera V4L2 (fps)')

        """
        Print info
        """
        cp = v4l2_capability()
        ioctl(self._fd, VIDIOC_QUERYCAP, cp)

        print("Opened v4l2 device '%s':" % self._fd.name)
        print("\tDriver:  %s" % _ubyte_to_str(cp.driver))
        print("\tCard:    %s" % _ubyte_to_str(cp.card))
        print("\tBusinfo: %s" % _ubyte_to_str(cp.bus_info))

        """
        Handle configuration
        """
        fmt = v4l2_format()
        fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        ioctl(self._fd, VIDIOC_G_FMT, fmt)

        parm = v4l2_streamparm()
        parm.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        parm.parm.capture.capability = V4L2_CAP_TIMEPERFRAME
        ioctl(self._fd, VIDIOC_G_PARM, parm)

        if config.format not in ['mjpeg', 'jpeg']:
            raise Exception("Unsupported format: %s" % config.format)
        fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_MJPEG

        if 'resolution' in config.options:
            fmt.fmt.pix.width, fmt.fmt.pix.height = \
                config.options['resolution']

        quality = 100
        if 'quality' in config.options:
            quality = config.options['quality']

        self._proc = None
        if config.format in ['mjpeg', 'jpeg']:
            self._proc = _JPEGStripper(self._on_frame)
            self._on_frame = self._proc.on_frame

        self._time_per_frame = 0.
        if 'framerate' in config.options:
            parm.parm.capture.timeperframe.numerator = 1
            parm.parm.capture.timeperframe.denominator = \
                config.options['framerate']
            self._time_per_frame = 1./config.options['framerate']


        ioctl(self._fd, VIDIOC_S_FMT, fmt)
        ioctl(self._fd, VIDIOC_S_PARM, parm)
        ioctl(self._fd, VIDIOC_G_FMT, fmt)
        ioctl(self._fd, VIDIOC_G_PARM, parm)

        fps = parm.parm.capture.timeperframe.denominator /\
               parm.parm.capture.timeperframe.numerator

        print("Video config:")
        print("\tresolution: %d/%d" % (fmt.fmt.pix.width, fmt.fmt.pix.height))
        print("\tformat:     %s" % v4l2_fourcc_to_str(fmt.fmt.pix.pixelformat))
        print("\tsizeimage:  %d" % fmt.fmt.pix.sizeimage)
        print("\tfps:        %s" % fps)


        """
        Allocate buffers
        """
        req = v4l2_requestbuffers()
        req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        req.memory = V4L2_MEMORY_MMAP
        req.count = num_buffers
        ioctl(self._fd, VIDIOC_REQBUFS, req)

        self._buffers = []

        for i in range(req.count):
            buf = v4l2_buffer()
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = V4L2_MEMORY_MMAP
            buf.index = i
            ioctl(self._fd, VIDIOC_QUERYBUF, buf)

            mm = mmap.mmap(self._fd.fileno(),
                           buf.length,
                           mmap.MAP_SHARED,
                           mmap.PROT_READ | mmap.PROT_WRITE,
                           offset=buf.m.offset)
            ioctl(self._fd, VIDIOC_QBUF, buf)
            self._buffers.append(mm)

    def run(self):
        """
        Start stream
        """
        ioctl(self._fd, VIDIOC_STREAMON,
              v4l2_buf_type(V4L2_BUF_TYPE_VIDEO_CAPTURE))
        select.select([self._fd], [], [])

        """
        Main loop
        """
        last_frame = 0
        while self._running:
            """
            FPS Limiter
            """
            while (time.time() - last_frame) < self._time_per_frame:
                time.sleep(0.001)
            last_frame = time.time()

            buf = v4l2_buffer()
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = V4L2_MEMORY_MMAP

            """
            Asynchronous processing => Copy
            """
            ioctl(self._fd, VIDIOC_DQBUF, buf)
            frame = bytes(self._buffers[buf.index])
            ioctl(self._fd, VIDIOC_QBUF, buf)

            self._raw_fps.register(1.)
            self._on_frame(frame)

        """
        Stop stream
        """
        ioctl(self._fd, VIDIOC_STREAMOFF,
              v4l2_buf_type(V4L2_BUF_TYPE_VIDEO_CAPTURE))
        """
        Cleanup
        """
        for b in self._buffers:
            b.close()

        if self._proc is not None:
            self._proc.close()

    def stop(self):
        self._running = False


class V4L2Cam(PythonSpaceCamera):
    def __init__(self, gallery, ws_port):
        super().__init__(gallery, ws_port)
        self._fd = None
        self._stream = None

    """
    PythonSpaceCamera API
    """
    def _py_image(self, config, path):
        class _:
            def __init__(self, path):
                self._path = path
                self._counter = 0
                self.stream = None

            def on_frame(self, frame):
                self._counter += 1
                if self._counter == 10:
                    self.stream.stop()
                    with open(self._path, 'wb') as img:
                        img.write(frame)

        closure = _(path)

        fd = open("/dev/video0", "rb+", buffering=0)
        stream = _Stream(fd, config, closure.on_frame)
        closure.stream = stream
        stream.start()
        stream.join()
        fd.close()

    def _py_start(self, config):
        if self._fd is not None or self._stream is not None:
            raise Exception("Call _py_stop first!")
        self._fd = open("/dev/video0", "rb+", buffering=0)
        self._stream = _Stream(self._fd, config, self._on_frame)
        self._stream.start()

    def _py_stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.join()
            self._fd.close()

            self._stream = None
            self._fd = None

    def _py_close(self):
        self._py_stop()
