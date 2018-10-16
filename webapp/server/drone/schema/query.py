import graphene


class Query(graphene.ObjectType):
    tmp = graphene.String()

    def resolve_tmp(self, info):
        return str(info.context['server'])
