import os
import signal
import traceback
from subprocess import Popen, PIPE

CMAVNODE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "..", "..", "cpp", "cmavnode", "build", "cmavnode")
CMAVNODE_CONFIG = "/tmp/cmavnode.conf"


class MAVLinkProxy:
    def __init__(self, master_port):
        self._master_port = master_port
        self._addr = None
        self._process = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def set_proxy(self, addr):
        self._addr = addr
        ip, port = addr.split(":")
        self.close()
        with open(CMAVNODE_CONFIG, "w") as config:
            config.write("[master]\n" +
                         "type=serial\n" + 
                         ("port=%s\n" % self._master_port) + 
                         "baud=115200\n")
            config.write("[slave]\n" +
                         "type=socket\n" + 
                         ("targetip=%s\n" % ip) + 
                         ("targetport=%s\n" % port))
        self._process = Popen((CMAVNODE_PATH + " -f " + CMAVNODE_CONFIG).split(" "))

    def get_proxy(self):
        return self._addr

    def close(self):
        if self._process is not None:
            """
            Try SIGINT
            """
            pid = self._process.pid
            os.kill(pid, signal.SIGINT)
            if self._process.poll():
                self._process.terminate()
            self._process = None

if __name__ == '__main__':
    import time
    with MAVLinkProxy("/dev/ttyAMA0") as proxy:
        proxy.set_proxy("172.16.0.106:14550")
        time.sleep(3)
