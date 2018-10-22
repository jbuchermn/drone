import traceback
from flask import Flask, render_template, send_from_directory, request
from flask_graphql import GraphQLView
import random


from .schema import schema
from .camera.gallery import Gallery
from .camera.raspicam import RaspiCam
from .quad.mavlink_proxy import MAVLinkProxy
from .util.ping import Ping


class Server:
    def __init__(self):
        self.gallery = Gallery('/home/pi/Camera')
        self.gallery.observe()

        self.cam = RaspiCam(self.gallery, ws_port=8088)
        self.cam.start(mode='stream')

        self.mavlink_proxy = MAVLinkProxy("/dev/ttyAMA0")

        self.client_ip = None
        self.client_ping = None

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
        if self.client_ping is not None:
            self.client_ping.close()


def run(*args, **kwargs):
    with Server() as server:
        app = Flask(__name__,
                    static_folder='../../client',
                    static_url_path='',
                    template_folder='../../client')

        @app.route('/')
        def index():
            return render_template("index.html",
                                   rand=random.randint(1, 100000))

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

        app.run(*args, **kwargs)
