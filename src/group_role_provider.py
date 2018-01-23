from authz_association_provider import AuthzAssociationProvider

provider = AuthzAssociationProvider('Custom::Authz0GroupRole', 'group', 'role')


def handler(request, context):
    return provider.handle(request, context)
