import graphene
import json


class Camera(graphene.ObjectType):
    def __init__(self, server):
        self._server = server

    config = graphene.String()
    ws_port = graphene.Int()

    def resolve_config(self, info):
        config = self._server.cam.current_config()
        return json.dumps(config)

    def resolve_ws_port(self, info):
        return self._server.cam_broadcast.port

