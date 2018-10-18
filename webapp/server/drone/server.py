import traceback
from flask import Flask, render_template, send_from_directory
from flask_graphql import GraphQLView
import random


from .schema import schema
from .ws_broadcast import WSBroadcast
from .camera.gallery import Gallery
from .camera.raspicam import RaspiCam
from .quad.mav import MAV


class Server:
    def __init__(self):
        self.gallery = Gallery('/home/pi/Camera')
        self.gallery.observe()

        self.cam_broadcast = WSBroadcast('cam', 8088)
        self.cam_broadcast.start()

        self.cam = RaspiCam(self.gallery)
        self.cam.on_frame(self.cam_broadcast.message)
        self.cam.start(mode='stream')

        self.mav = MAV(conn="/dev/ttyAMA0", baud=115200)
        self.mav.set_proxy("172.16.0.106:14550")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self.gallery.close()
        self.cam_broadcast.stop()
        self.cam.close()
        self.mav.close()


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

        app.add_url_rule('/graphql',
                         view_func=GraphQLView.as_view(
                             'graphql',
                             schema=schema,
                             graphiql=True,
                             get_context=lambda: {'server': server}))

        app.run(*args, **kwargs)
