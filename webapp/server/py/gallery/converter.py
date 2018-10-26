from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue
import time
import os

from ..util import is_file_write_in_progress


class ConverterJob:
    def __init__(self, entry, source_file, target_file, command):
        self._entry = entry
        self.source_file = source_file
        self.target_file = target_file
        self.command = command

    def run(self):
        print("Converting %s..." % self.command)
        p = Popen(self.command.split(" "), stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        success = (p.returncode == 0) and os.path.isfile(self.target_file)

        if success:
            self._entry.on_job_complete()
        else:
            raise Exception("Conversion failed: %s" % stderr.decode("utf-8"))


class Converter(Thread):
    def __init__(self):
        super().__init__()
        self._jobs = Queue()
        self._running = True

        self._corrupt_files = []

    def run(self):
        while self._running:
            if is_file_write_in_progress():
                time.sleep(5)
                continue

            if self._jobs.empty():
                time.sleep(1)
                continue

            job = self._jobs.get()
            if job.source_file in self._corrupt_files:
                continue

            try:
                job.run()
                print("...done")
            except Exception as err:
                """
                Don't run the same conversion indefinitely
                """
                print("...failed:\n%s" % err)
                self._corrupt_files += [job.source_file]

    def add_job(self, job):
        self._jobs.put(job)

    def close(self):
        self._running = False
