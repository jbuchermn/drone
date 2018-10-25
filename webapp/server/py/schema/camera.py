import graphene
import json

from ..camera import StreamingMode


class CameraType(graphene.ObjectType):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server

    id = graphene.String()
    config = graphene.String()
    ws_port = graphene.Int()
    recording = graphene.Boolean()

    def resolve_config(self, info):
        config = self._server.cam.get_current_config()
        return json.dumps(config)

    def resolve_ws_port(self, info):
        return self._server.cam.ws_port

    def resolve_recording(self, info):
        return self._server.cam.get_current_streaming_mode in \
            [StreamingMode.FILE, StreamingMode.BOTH]
