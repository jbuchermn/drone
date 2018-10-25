import os
import time
from threading import Thread

from .converter import Converter
from .entry import Entry


class Gallery:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        for f in ['img', 'vid', 'thumbnail', 'backup']:
            folder = os.path.join(self.root_dir, f)
            if not os.path.exists(folder):
                os.makedirs(folder)

        self._converter = Converter()
        self._converter.start()
        
        self._entries = list(self._load_entries())
        """
        See if there is some post-processing left
        """
        for e in self._entries:
            e.process()

    def _load_entries(self):
        kind_name = set()
        for kind in ['img', 'vid']:
            for n in os.listdir(os.path.join(self.root_dir, kind)):
                f = os.path.join(self.root_dir, kind, n)
                yield Entry(self, kind, new=False, filename=f)


    def add_job(self, job):
        self._converter.add_job(job)

    def close(self):
        self._converter.close()

    def new_image(self, format='jpg'):
        e = Entry(self, 'img', new=True, format=format)
        self._entries += [e]
        return e

    def new_video(self, format='mjpeg'):
        e = Entry(self, 'vid', new=True, format=format)
        self._entries += [e]
        return e

    def list(self):
        return [e for e in self._entries if e.is_ready()]


