from authz_association_provider import AuthzAssociationProvider

provider = AuthzAssociationProvider('Custom::Authz0UserRole', 'user', 'role')


def handler(request, context):
    return provider.handle(request, context)
