import graphene
import json

from ..camera import StreamingMode


class CameraType(graphene.ObjectType):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server

    id = graphene.String()
    image_config = graphene.String()
    video_config = graphene.String()
    stream_config = graphene.String()
    ws_port = graphene.Int()
    recording = graphene.Boolean()
    streaming = graphene.Boolean()

    def resolve_image_config(self, info):
        config = self._server.cam.get_image_config()
        return json.dumps(None if config is None else config.get_dict())

    def resolve_video_config(self, info):
        config = self._server.cam.get_video_config()
        return json.dumps(None if config is None else config.get_dict())

    def resolve_stream_config(self, info):
        config = self._server.cam.get_stream_config()
        return json.dumps(None if config is None else config.get_dict())

    def resolve_ws_port(self, info):
        return self._server.cam.ws_port

    def resolve_recording(self, info):
        return self._server.cam.get_current_streaming_mode() in \
            [StreamingMode.FILE, StreamingMode.BOTH]

    def resolve_streaming(self, info):
        return self._server.cam.get_current_streaming_mode() in \
            [StreamingMode.STREAM, StreamingMode.BOTH]
