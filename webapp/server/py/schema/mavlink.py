import graphene


class MAVLinkProxyType(graphene.ObjectType):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server

    id = graphene.String()
    addr = graphene.String()

    def resolve_addr(self, info):
        return self._server.mavlink_proxy.get_proxy()
