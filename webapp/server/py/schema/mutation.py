import graphene
import json

from .gallery import GalleryType
from .camera import CameraType
from .mavlink import MAVLinkProxyType
from ..camera import StreamingMode, CameraConfig


class CameraGalleryType(graphene.ObjectType):
    gallery = graphene.Field(GalleryType)
    camera = graphene.Field(CameraType)


class Mutation(graphene.ObjectType):
    cameraStart = graphene.Field(CameraGalleryType, record=graphene.Boolean(), stream=graphene.Boolean())
    cameraStop = graphene.Field(CameraGalleryType)
    cameraImage = graphene.Field(CameraGalleryType)
    cameraSetStreamConfig = graphene.Field(CameraGalleryType, config=graphene.String())
    cameraSetVideoConfig = graphene.Field(CameraGalleryType, config=graphene.String())
    cameraSetImageConfig = graphene.Field(CameraGalleryType, config=graphene.String())

    startMAVLinkProxy = graphene.Field(MAVLinkProxyType,
                                       addr=graphene.String(required=False))
    stopMAVLinkProxy = graphene.Field(MAVLinkProxyType)

    autoHotspot = graphene.Field(graphene.Int, config=graphene.String())
    shutdownServer = graphene.Field(graphene.Int)

    def resolve_cameraStart(self, info, record, stream):
        server = info.context['server']
        mode = None
        if record and stream:
            mode = StreamingMode.BOTH
        elif record and not stream:
            mode = StreamingMode.FILE
        elif not record and stream:
            mode = StreamingMode.STREAM
        else:
            raise Exception("Call cameraStop")
        server.cam.start(mode)
        return CameraGalleryType(
            camera=CameraType(server, id="1"),
            gallery=GalleryType(server, id="1")
        )

    def resolve_cameraStop(self, info):
        server = info.context['server']
        server.cam.stop()
        return CameraGalleryType(
            camera=CameraType(server, id="1"),
            gallery=GalleryType(server, id="1")
        )

    def resolve_cameraImage(self, info):
        server = info.context['server']
        server.cam.image()
        return CameraGalleryType(
            camera=CameraType(server, id="1"),
            gallery=GalleryType(server, id="1")
        )

    def resolve_cameraSetStreamConfig(self, info, config):
        server = info.context['server']
        config = json.loads(config)
        server.cam.set_stream_config(CameraConfig(**config))

    def resolve_cameraSetVideoConfig(self, info, config):
        server = info.context['server']
        config = json.loads(config)
        server.cam.set_video_config(CameraConfig(**config))

    def resolve_cameraSetImageConfig(self, info, config):
        server = info.context['server']
        config = json.loads(config)
        server.cam.set_image_config(CameraConfig(**config))

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
