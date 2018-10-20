import graphene

from .camera import CameraType
from .gallery import GalleryType
from .mavlink import MAVLinkProxyType


class Query(graphene.ObjectType):
    camera = graphene.Field(CameraType)
    gallery = graphene.Field(GalleryType)
    mavlinkProxy = graphene.Field(MAVLinkProxyType)

    def resolve_camera(self, info):
        server = info.context['server']
        return CameraType(server, id="1")

    def resolve_gallery(self, info):
        server = info.context['server']
        return GalleryType(server, id="1")

    def resolve_mavlinkProxy(self, info):
        server = info.context['server']
        return MAVLinkProxyType(server, id="1")
