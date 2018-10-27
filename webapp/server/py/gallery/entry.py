import os
from datetime import datetime
from PIL import Image

from .converter import ConverterJob

_containers = {
    'h264': ['mp4', 'ffmpeg -y -i %s -vcodec copy %s'],
    'mjpeg': ['avi', 'ffmpeg -y -i %s -vcodec copy %s'],
}

_thumbnails = {
    'mp4': ['jpeg', 'ffmpeg -y -i %s -vf select=eq(n\\,0),scale=-1:240 -v:frames 1 %s'],  # noqa E501
    'avi': ['jpeg', 'ffmpeg -y -i %s -vf select=eq(n\\,0),scale=-1:240 -v:frames 1 %s'],  # noqa E501
    'jpeg': ['jpeg', 'convert -thumbnail x240 %s %s'],
}


class Entry:
    def __init__(self, gallery, kind, new=False, format=None, filename=None):
        self._gallery = gallery
        self.kind = kind

        if new:
            if format is None or filename is not None:
                raise Exception("Parameters mismatch")
            self.format = format
            self.name = datetime.now().isoformat()
            self._ready = False
        else:
            self.format = filename.split(".")[-1]
            self.name = os.path.basename(filename)[:-len(self.format)-1]

        self.thumbnail = {
            'path': os.path.join(self._gallery.root_dir, 'thumbnail',
                                 self.name + '.jpg'),
            'found': False,
            'width': None,
            'height': None
        }
        self._find_thumbnail()

        """
        Post-processing state
        """
        self._container_target = None

    def filename(self):
        """
        Getter
        """
        return os.path.join(self._gallery.root_dir, self.kind,
                            self.name + '.' + self.format)

    def _find_thumbnail(self):
        if os.path.isfile(self.thumbnail['path']):
            with Image.open(self.thumbnail['path']) as img:
                width, height = img.size
                self.thumbnail['width'] = width
                self.thumbnail['height'] = height
                self.thumbnail['found'] = True

    def is_ready(self):
        """
        Is post-processing done?
        """
        return self.format not in _containers.keys() and \
            self.thumbnail['found']

    def process(self):
        """
        Called once the file is ready for post-processing
        """
        if self.format in _containers.keys():
            """
            Convert to /tmp, only copy after success
            """
            ext, cmd = _containers[self.format]
            target = os.path.join('/tmp', self.name + '.' + ext)
            cmd = cmd % (self.filename(), target)
            self._gallery.add_job(ConverterJob(self, self.filename(),
                                               target, cmd))

            self._container_target = target

        elif not self.thumbnail['found']:
            ext, cmd = _thumbnails[self.format]
            cmd = cmd % (self.filename(), self.thumbnail['path'])
            self._gallery.add_job(ConverterJob(self, self.filename(),
                                               self.thumbnail['path'], cmd))

    def on_job_complete(self):
        if self._container_target is not None and \
                os.path.isfile(self._container_target):
            os.rename(self.filename(), os.path.join(
                self._gallery.root_dir, 'backup', self.name + self.format))
            self.format = _containers[self.format][0]
            os.rename(self._container_target, self.filename())
            self._container_target = None

            """
            Post-processing is not yet done
            """
            self.process()
        else:
            self._find_thumbnail()





