import graphene
import json


class CameraType(graphene.ObjectType):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server

    id = graphene.String()
    config = graphene.String()
    ws_port = graphene.Int()

    def resolve_config(self, info):
        config = self._server.cam.current_config()
        return json.dumps(config)

    def resolve_ws_port(self, info):
        return self._server.cam.get_ws_port()

