import logging
import json
import requests
import group_nested_provider
import group_member_provider
import group_role_provider
import user_role_provider
import group_mapping_provider

from auth0_provider import Auth0Provider


log = logging.getLogger(name=__name__)


class Authz0Provider(Auth0Provider, object):
    """
    Generic Cloudformation custom resource provider for Auth0 Authorization Extension resources.

    Auth0 authorization has a different API, and uses PUT instead of PATCH to update objects.

    In addition, posting a duplicate group name does work :-(
    """

    def __init__(self):
        super(Authz0Provider, self).__init__()

    def is_supported_resource_type(self):
        return self.resource_type.startswith('Custom::Authz0')

    @property
    def audience(self):
        return 'urn:auth0-authz-api'

    @property
    def url(self):
        return '%s/api/%s' % (self.authz_url, self.auth0_resource_name)

    def set_attributes_from_returned_value(self, value):
        self.physical_resource_id = value['_id']

    def get_all_values(self):
        """
        returns all values of this resource type
        """
        self.add_authorization_header()
        r = requests.get(self.url, headers=self.headers)
        if r.status_code == 200:
            return r.json()
        else:
            msg = 'failed to retrieve {} from {} with status code {}, {}'.format(
                self.auth0_resource_name, r.url, r.status_code, r.text)
            raise ValueError(msg)

    def group_exists(self):
        value = self.get('Value')
        matches = []
        if self.auth0_resource_name == 'groups' and 'name' in value:
            all_values = self.get_all_values()
            matches = list(filter(lambda v: 'name' in v and v['name'] == value['name'], all_values['groups']))
        return len(matches) > 0

    def create(self):
        if self.auth0_resource_name == 'groups' and self.group_exists():
            self.physical_resource_id = 'could-not-create'
            self.fail('group already exists.')
        else:
            super(Authz0Provider, self).create()

    @property
    def rest_update_operation(self):
        return 'PUT'


provider = Authz0Provider()


def handler(request, context):
    if request['ResourceType'] == 'Custom::Authz0GroupMember':
        return group_member_provider.handler(request, context)
    elif request['ResourceType'] == 'Custom::Authz0GroupRole':
        return group_role_provider.handler(request, context)
    elif request['ResourceType'] == 'Custom::Authz0UserRole':
        return user_role_provider.handler(request, context)
    elif request['ResourceType'] == 'Custom::Authz0GroupNested':
        return group_nested_provider.handler(request, context)
    elif request['ResourceType'] == 'Custom::Authz0GroupMapping':
        return group_mapping_provider.handler(request, context)
    else:
        return provider.handle(request, context)
