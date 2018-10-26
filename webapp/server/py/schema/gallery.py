import os
import graphene


class GalleryEntryType(graphene.ObjectType):
    id = graphene.String()
    kind = graphene.String()
    name = graphene.String()
    path = graphene.String()
    thumbnail_path = graphene.String()
    thumbnail_width = graphene.Int()
    thumbnail_height = graphene.Int()

    def __init__(self, entry, gallery):
        self._entry = entry
        self._gallery = gallery

        self.name = entry.name
        self.id = entry.name
        self.kind = entry.kind

    def resolve_path(self, info):
        return os.path.relpath(self._entry.filename(), self._gallery.root_dir)

    def resolve_thumbnail_path(self, info):
        return os.path.relpath(self._entry.thumbnail['path'],
                               self._gallery.root_dir)

    def resolve_thumbnail_width(self, info):
        return self._entry.thumbnail['width']

    def resolve_thumbnail_height(self, info):
        return self._entry.thumbnail['height']


class GalleryType(graphene.ObjectType):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server

    id = graphene.String()
    entries = graphene.List(GalleryEntryType)

    def resolve_entries(self, info):
        for e in self._server.gallery.list():
            yield GalleryEntryType(e, self._server.gallery)
