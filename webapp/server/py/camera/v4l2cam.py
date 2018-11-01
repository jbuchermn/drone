from fcntl import ioctl
from threading import Thread
from PIL import Image
from io import BytesIO
import mmap
import time
import select

from ..util import Stream

from .python_space_camera import PythonSpaceCamera
from .v4l2 import (
    v4l2_fourcc_to_str,
    v4l2_capability,
    v4l2_format,
    v4l2_streamparm,
    v4l2_requestbuffers,
    v4l2_buffer,
    v4l2_buf_type,
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
    V4L2_BUF_TYPE_VIDEO_CAPTURE,
    V4L2_MEMORY_MMAP,
    V4L2_CAP_TIMEPERFRAME,
    V4L2_PIX_FMT_MJPEG,
)


def _ubyte_to_str(arr):
    return "".join([chr(c) for c in arr])


class _FPSLimit:
    def __init__(self, fps, on_frame):
        self._tpf = 1./fps
        self._on_frame = on_frame
        self._last = 0

    def on_frame(self, frame):
        ts = time.time()
        if ts > self._last + self._tpf:
            self._on_frame(frame)
            self._last = ts


class _JPEGProcessor:
    def __init__(self, quality, on_frame):
        self._quality = quality
        self._on_frame = on_frame
        self._counter = 0
        self._stream = Stream('JPEG processor (ms)')

    def on_frame(self, frame):
        try:
            src = Image.open(BytesIO(frame))
            result = BytesIO()
            t_comp = time.time()

            """
            Hardcoded configuration. But why would we ever want to change this value?
            """
            src = src.rotate(180)
            src.save(result, "JPEG", quality=self._quality)
            t_comp = time.time() - t_comp
            self._on_frame(result.getvalue())
        except Exception:
            """
            Don't dispatch unprocessed frames
            """
            pass


        self._counter += 1
        if self._counter % 10 == 0:
            self._stream.register(1000 * t_comp)


class _Stream(Thread):
    def __init__(self, fd, config, on_frame, num_buffers=2):
        super().__init__()
        self._fd = fd
        self._on_frame = on_frame
        self._running = True

        """
        Print info
        """
        self._cp = v4l2_capability()
        ioctl(self._fd, VIDIOC_QUERYCAP, self._cp)

        print("Opened v4l2 device '%s':" % self._fd.name)
        print("\tDriver:  %s" % _ubyte_to_str(self._cp.driver))
        print("\tCard:    %s" % _ubyte_to_str(self._cp.card))
        print("\tBusinfo: %s" % _ubyte_to_str(self._cp.bus_info))

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

        if config.format != 'mjpeg':
            raise Exception("Unsupported format: %s" % config.format)
        fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_MJPEG

        if 'resolution' in config.options:
            fmt.fmt.pix.width, fmt.fmt.pix.height = \
                config.options['resolution']

        quality = 100
        if 'quality' in config.options:
            quality = config.options['quality']

        if config.format == 'mjpeg':
            comp = _JPEGProcessor(quality, self._on_frame)
            self._on_frame = comp.on_frame

        if 'framerate' in config.options:
            parm.parm.capture.timeperframe.numerator = 1
            parm.parm.capture.timeperframe.denominator = \
                config.options['framerate']

            """
            Framerate setting might pick highest possible rate
            """
            fps = _FPSLimit(config.options['framerate'], self._on_frame)
            self._on_frame = fps.on_frame

        ioctl(self._fd, VIDIOC_S_FMT, fmt)
        ioctl(self._fd, VIDIOC_S_PARM, parm)
        ioctl(self._fd, VIDIOC_G_FMT, fmt)
        ioctl(self._fd, VIDIOC_G_PARM, parm)

        print("Video config:")
        print("\tresolution: %d/%d" % (fmt.fmt.pix.width, fmt.fmt.pix.height))
        print("\tformat:     %s" % v4l2_fourcc_to_str(fmt.fmt.pix.pixelformat))
        print("\tsizeimage:  %d" % fmt.fmt.pix.sizeimage)
        print("\tfps:        %s" %
              (parm.parm.capture.timeperframe.denominator /
               parm.parm.capture.timeperframe.numerator))

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
        while self._running:
            buf = v4l2_buffer()
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = V4L2_MEMORY_MMAP

            ioctl(self._fd, VIDIOC_DQBUF, buf)
            self._on_frame(self._buffers[buf.index])
            ioctl(self._fd, VIDIOC_QBUF, buf)

        """
        Stop stream
        """
        ioctl(self._fd, VIDIOC_STREAMOFF,
              v4l2_buf_type(V4L2_BUF_TYPE_VIDEO_CAPTURE))

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
        raise Exception("Unsupported atm")

    def _py_start(self, config):
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
