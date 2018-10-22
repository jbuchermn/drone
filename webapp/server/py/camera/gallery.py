import os
import time
from threading import Thread


CONVERSIONS = {
    'h264': ['mp4', 'ffmpeg -y -i %s -vcodec copy %s'],
    'mjpeg': ['avi', 'ffmpeg -y -i %s -vcodec copy %s'],
}


class GalleryObserver(Thread):
    def __init__(self, gallery):
        super().__init__()
        self.gallery = gallery
        self.running = True

    def _handle_file(self, filename):
        ext = filename.split(".")[-1]
        conversion = CONVERSIONS[ext]
        new_filename = filename.replace("vid_raw", "vid")[:-len(ext)] \
            + conversion[0]
        command = conversion[1] % (filename, new_filename)

        if not os.path.isfile(new_filename):
            print(command)
            os.system(command)

    def run(self):
        while self.running:
            files = os.listdir(os.path.join(self.gallery.root_dir, 'vid_raw'))
            for f in files:
                """
                Skip files starting with . (these are internal in RaspiCam,
                i. e. still opened)
                """
                if f.split(".")[-1] in CONVERSIONS and f[0] != ".":
                    self._handle_file(
                        os.path.join(self.gallery.root_dir, 'vid_raw', f))
            time.sleep(2)

    def close(self):
        self.running = False


class Gallery:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self._observer = GalleryObserver(self)

        for f in ['img', 'vid', 'vid_raw']:
            folder = os.path.join(self.root_dir, f)
            if not os.path.exists(folder):
                os.makedirs(folder)

    def close(self):
        if self._observer is not None:
            self._observer.close()

    def observe(self):
        self._observer.start()

    def new_image(self, format='jpg'):
        folder = os.path.join(self.root_dir, 'img')
        filename = '%d.%s' % (time.time()*1000, format)
        return os.path.join(folder, filename)

    def new_video(self, format='mjpeg'):
        folder = os.path.join(self.root_dir, 'vid_raw')
        filename = '%d.%s' % (time.time()*1000, format)
        return os.path.join(folder, filename)

    def list(self):
        img = [f for f in os.listdir(os.path.join(self.root_dir, 'img'))
               if os.path.isfile(os.path.join(self.root_dir, 'img', f))]
        vid = [f for f in os.listdir(os.path.join(self.root_dir, 'vid'))
               if os.path.isfile(os.path.join(self.root_dir, 'vid', f))]

        result = [('img', i) for i in img] + [('vid', v) for v in vid]
        return sorted(result, key=lambda v: v[1])


