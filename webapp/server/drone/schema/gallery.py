import graphene


class GalleryEntryType(graphene.ObjectType):
    id = graphene.String()
    kind = graphene.String()
    name = graphene.String()


class GalleryType(graphene.ObjectType):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server

    id = graphene.String()
    entries = graphene.List(GalleryEntryType)

    def resolve_entries(self, info):
        for t, n in self._server.gallery.list():
            yield GalleryEntryType(id=t + n, kind=t, name=n)
