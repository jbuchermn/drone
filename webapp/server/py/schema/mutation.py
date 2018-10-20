import graphene
import json

from .gallery import GalleryType
from .camera import CameraType
from .mavlink import MAVLinkProxyType


class CameraGalleryType(graphene.ObjectType):
    gallery = graphene.Field(GalleryType)
    camera = graphene.Field(CameraType)


class Mutation(graphene.ObjectType):
    startStream = graphene.Field(CameraGalleryType, config=graphene.String())
    takePicture = graphene.Field(CameraGalleryType, config=graphene.String())
    takeVideo = graphene.Field(CameraGalleryType, stream=graphene.Boolean(),
                               config=graphene.String())

    startMAVLinkProxy = graphene.Field(MAVLinkProxyType, addr=graphene.String())

    def resolve_startStream(self, info, config):
        server = info.context['server']
        config = json.loads(config)
        server.cam.start(mode='stream', **config)
        return CameraGalleryType(
            camera=CameraType(server, id="1"),
            gallery=GalleryType(server, id="1")
        )

    def resolve_takePicture(self, info, config):
        server = info.context['server']
        config = json.loads(config)
        server.cam.image(**config)
        return CameraGalleryType(
            camera=CameraType(server, id="1"),
            gallery=GalleryType(server, id="1")
        )

    def resolve_takeVideo(self, info, stream, config):
        server = info.context['server']
        config = json.loads(config)
        mode = 'both' if stream else 'file'
        server.cam.start(mode=mode, **config)
        return CameraGalleryType(
            camera=CameraType(server, id="1"),
            gallery=GalleryType(server, id="1")
        )

    def resolve_startMAVLinkProxy(self, info, addr):
        server = info.context['server']
        server.mavlink_proxy.set_proxy(addr)
        return MAVLinkProxyType(server, id="1")
