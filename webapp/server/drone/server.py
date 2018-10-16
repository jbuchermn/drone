import traceback
from flask import Flask, render_template
from flask_graphql import GraphQLView
import random


from .ws_broadcast import WSBroadcast
from .raspicam import RaspiCam
from .schema import schema


class Server:
    def __init__(self):
        self._cam = RaspiCam()
        self._cam_broadcast = WSBroadcast('cam', 8088)
        self._cam_broadcast.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        self._cam.close()
        self._cam_broadcast.stop()


def run(*args, **kwargs):
    with Server() as server:
        app = Flask(__name__,
                    static_folder='../client/dist',
                    template_folder='../client')

        @app.route('/')
        def index():
            return render_template("index.html",
                                   rand=random.randint(1, 100000))

        app.add_url_rule('/graphql',
                         view_func=GraphQLView.as_view(
                             'graphql',
                             schema=schema,
                             graphiql=True,
                             get_context=lambda: {'server': server}))

        app.run(*args, **kwargs)
