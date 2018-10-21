import graphene


class StreamType(graphene.ObjectType):
    def __init__(self, stream, **kwargs):
        super().__init__(**kwargs)
        self._stream = stream

    id = graphene.String()
    name = graphene.String()
    t = graphene.List(graphene.Float)
    val = graphene.List(graphene.Float)

    def resolve_id(self, info):
        return self._stream.name

    def resolve_name(self, info):
        return self._stream.name

    def resolve_t(self, info):
        return self._stream.t

    def resolve_val(self, info):
        return self._stream.val
