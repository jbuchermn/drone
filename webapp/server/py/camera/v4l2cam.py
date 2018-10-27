from fcntl import ioctl
from threading import Thread
import mmap
import time
import select

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
    V4L2_CAP_TIMEPERFRAME
)


def _ubyte_to_str(arr):
    return "".join([chr(c) for c in arr])


class _Config:
    def __init__(self, fd):
        self._fd = fd

        fmt = v4l2_format()
        fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        ioctl(self._fd, VIDIOC_G_FMT, fmt)

        parm = v4l2_streamparm()
        parm.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        parm.parm.capture.capability = V4L2_CAP_TIMEPERFRAME
        ioctl(self._fd, VIDIOC_G_PARM, parm)

        print("Current video config:")
        print("\tresolution: %d/%d" % (fmt.fmt.pix.width, fmt.fmt.pix.height))
        print("\tformat:     %s" % v4l2_fourcc_to_str(fmt.fmt.pix.pixelformat))
        print("\tsizeimage:  %d" % fmt.fmt.pix.sizeimage)
        print("\tfps:        %s" %
              (parm.parm.capture.timeperframe.denominator /
               parm.parm.capture.timeperframe.numerator))

        fmt.fmt.pix.width = 640
        fmt.fmt.pix.height = 480
        ioctl(self._fd, VIDIOC_S_FMT, fmt)

        # possibly set fps is larger than this value
        parm.parm.capture.timeperframe.numerator = 1
        parm.parm.capture.timeperframe.denominator = 10
        ioctl(self._fd, VIDIOC_S_PARM, parm)


class _Buffers:
    def __init__(self, fd, count):
        self._fd = fd

        req = v4l2_requestbuffers()
        req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        req.memory = V4L2_MEMORY_MMAP
        req.count = count
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

    def get_data(self, index):
        return self._buffers[index]


class _Capture(Thread):
    def __init__(self, fd, buffers, on_frame):
        super().__init__()
        self._running = True
        self._fd = fd
        self._buffers = buffers
        self._on_frame = on_frame
        self._finished = False

    def stop(self):
        self._running = False

    def is_finished(self):
        return self._finished

    def run(self):
        while self._running:
            buf = v4l2_buffer()
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = V4L2_MEMORY_MMAP

            ioctl(self._fd, VIDIOC_DQBUF, buf)
            self._on_frame(self._buffers.get_data(buf.index))
            ioctl(self._fd, VIDIOC_QBUF, buf)
        self._finished = True


class V4L2Cam(PythonSpaceCamera):
    def __init__(self, gallery, ws_port):
        super().__init__(gallery, ws_port)

        self._fd = open("/dev/video1", "rb+", buffering=0)
        self._cp = v4l2_capability()
        ioctl(self._fd, VIDIOC_QUERYCAP, self._cp)

        print("Opened v4l2 device '%s':" % self._fd.name)
        print("\tDriver:  %s" % _ubyte_to_str(self._cp.driver))
        print("\tCard:    %s" % _ubyte_to_str(self._cp.card))
        print("\tBusinfo: %s" % _ubyte_to_str(self._cp.bus_info))

        self._config = _Config(self._fd)
        self._buffers = _Buffers(self._fd, 3)
        self._capture = None

    def _streamon(self):
        ioctl(self._fd, VIDIOC_STREAMON,
              v4l2_buf_type(V4L2_BUF_TYPE_VIDEO_CAPTURE))
        select.select([self._fd], [], [])

    def _streamoff(self):
        ioctl(self._fd, VIDIOC_STREAMOFF,
              v4l2_buf_type(V4L2_BUF_TYPE_VIDEO_CAPTURE))

    """
    PythonSpaceCamera API
    """
    def _py_image(self, config, path):
        raise Exception("Unsupported atm")

    def _py_start(self, config):
        self._streamon()
        self._capture = _Capture(self._fd, self._buffers, self._on_frame)
        self._capture.start()

    def _py_stop(self):
        if self._capture is not None:
            self._capture.stop()

        """
        Not waiting for capture will cause DQBUF
        to throw an exception
        """
        while not self._capture.is_finished():
            time.sleep(0.02)

        self._streamoff()

    def _py_close(self):
        self._py_stop()
        self._fd.close()
