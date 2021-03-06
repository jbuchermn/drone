import traceback
import subprocess
from threading import Thread
import os
import random
import time
import signal
from werkzeug.serving import make_server
from flask import Flask, render_template, send_from_directory, request
from flask_graphql import GraphQLView
import logging


from .schema import schema
from .gallery import Gallery
from .camera import Camera, StreamingMode
from .quad import MAVLinkProxy
from .util import Ping, shutdown, auto_hotspot
from .gpio import GPIOInterface


class Server:
    def __init__(self):
        self.gallery = Gallery('/home/pi/Camera')

        self.cam = Camera(self.gallery, ws_port=8088)
        self.mavlink_proxy = MAVLinkProxy("/dev/ttyS3")
        self.gpio = GPIOInterface(self)

        self.client_ip = None
        self.client_ping = None

        self.shutdown_requested = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def set_client_ip(self, ip):
        self.client_ip = ip
        if self.client_ping is not None:
            if self.client_ping.ip != self.client_ip:
                self.client_ping.close()
                self.client_ping = None

        if self.client_ping is None:
            self.client_ping = Ping(self.client_ip)
            self.client_ping.start()

    def close(self):
        self.gallery.close()
        self.cam.close()
        self.mavlink_proxy.close()
        self.gpio.close()
        if self.client_ping is not None:
            self.client_ping.close()

    def auto_hotspot(self, force):
        if self.cam.get_current_streaming_mode() == StreamingMode.STREAM or \
                self.cam.get_current_streaming_mode() == StreamingMode.BOTH:
            self.cam.stop()
        self.mavlink_proxy.close()
        if self.client_ping is not None:
            self.client_ping.close()

        auto_hotspot(force)

    def request_shutdown(self):
        self.shutdown_requested = True


class ServerThread(Thread):
    def __init__(self, app, host, port):
        super().__init__()
        print(host, port)
        self._srv = make_server(host, port, app)
        self._ctx = app.app_context()
        self._ctx.push()
        self.running = False

    def run(self):
        self.running = True
        self._srv.serve_forever()

    def shutdown(self):
        self._srv.shutdown()
        self.running = False


def run(host='0.0.0.0', port=5000):
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    shutdown_after_finish = False

    label = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
    print("Label: %s" % label)

    with Server() as server:
        app = Flask(__name__,
                    static_folder='../../client',
                    static_url_path='',
                    template_folder='../../client')

        @app.route('/')
        def index():
            return render_template("index.html",
                                   rand=label)

        @app.route('/gallery/<path:path>')
        def send_gallery(path):
            return send_from_directory(server.gallery.root_dir, path)

        def get_context():
            server.set_client_ip(request.remote_addr)
            return {'server': server}

        app.add_url_rule('/graphql',
                         view_func=GraphQLView.as_view(
                             'graphql',
                             schema=schema,
                             graphiql=True,
                             get_context=get_context))

        srv = ServerThread(app, host=host, port=port)
        print("Starting webserver up...")
        srv.start()

        """
        SIGINT (e.g. Ctrl-C) as graceful shutdown
        """
        def handle_sigint(sig, frame):
            print("Shutting webserver down...")
            srv.shutdown()
            print("...done")
        signal.signal(signal.SIGINT, handle_sigint)

        while srv.running:
            time.sleep(1)
            if server.shutdown_requested:
                shutdown_after_finish = True
                srv.shutdown()

    if shutdown_after_finish:
        shutdown()


