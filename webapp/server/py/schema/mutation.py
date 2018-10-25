import graphene
import json

from .gallery import GalleryType
from .camera import CameraType
from .mavlink import MAVLinkProxyType
from ..camera import StreamingMode
from ..camera import CameraConfig


class CameraGalleryType(graphene.ObjectType):
    gallery = graphene.Field(GalleryType)
    camera = graphene.Field(CameraType)


class Mutation(graphene.ObjectType):
    startStream = graphene.Field(CameraGalleryType, config=graphene.String())
    takePicture = graphene.Field(CameraGalleryType, config=graphene.String())
    takeVideo = graphene.Field(CameraGalleryType, stream=graphene.Boolean(),
                               config=graphene.String())

    startMAVLinkProxy = graphene.Field(MAVLinkProxyType,
                                       addr=graphene.String(required=False))
    stopMAVLinkProxy = graphene.Field(MAVLinkProxyType)

    autoHotspot = graphene.Field(graphene.Int, config=graphene.String())
    shutdownServer = graphene.Field(graphene.Int)

    def resolve_startStream(self, info, config):
        server = info.context['server']
        config = json.loads(config)
        server.cam.start(StreamingMode.STREAM, CameraConfig(config))
        return CameraGalleryType(
            camera=CameraType(server, id="1"),
            gallery=GalleryType(server, id="1")
        )

    def resolve_takePicture(self, info, config):
        server = info.context['server']
        config = json.loads(config)
        server.cam.image(CameraConfig(config))
        return CameraGalleryType(
            camera=CameraType(server, id="1"),
            gallery=GalleryType(server, id="1")
        )

    def resolve_takeVideo(self, info, stream, config):
        server = info.context['server']
        config = json.loads(config)
        mode = StreamingMode.BOTH if stream else StreamingMode.FILE
        server.cam.start(mode, CameraConfig(config))
        return CameraGalleryType(
            camera=CameraType(server, id="1"),
            gallery=GalleryType(server, id="1")
        )

    def resolve_startMAVLinkProxy(self, info, addr=None):
        server = info.context['server']
        if addr is None:
            addr = server.client_ip + ":14550"
        server.mavlink_proxy.set_proxy(addr)
        return MAVLinkProxyType(server, id="1")

    def resolve_stopMAVLinkProxy(self, info):
        server = info.context['server']
        server.mavlink_proxy.close()
        return MAVLinkProxyType(server, id="1")

    def resolve_shutdownServer(self, info):
        server = info.context['server']
        server.request_shutdown()
        return 0

    def resolve_autoHotspot(self, info, config):
        server = info.context['server']
        server.auto_hotspot(force=(config == "force"))
        return 0
