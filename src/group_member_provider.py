from authz_association_provider import AuthzAssociationProvider

provider = AuthzAssociationProvider('Custom::Authz0GroupMember', 'group', 'member')


def handler(request, context):
    return provider.handle(request, context)
