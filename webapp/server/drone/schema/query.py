import graphene

from .camera import Camera


class Query(graphene.ObjectType):
    camera = graphene.Field(Camera)

    def resolve_camera(self, info):
        server = info.context['server']
        return Camera(server)
