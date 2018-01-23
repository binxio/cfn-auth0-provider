from authz_association_provider import AuthzAssociationProvider

provider = AuthzAssociationProvider('Custom::Authz0GroupNested', 'group', 'nested', 'nested')


def handler(request, context):
    return provider.handle(request, context)
