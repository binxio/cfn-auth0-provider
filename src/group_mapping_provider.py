import re
import json
import requests

from auth0_provider import Auth0Provider
from auth0_provider import request_schema as auth0_request_schema

request_schema = json.loads(json.dumps(auth0_request_schema))
request_schema['properties']['Value'] = {
    "type": "object",
    "required": ["group", "groupName", "connectionName"],
    "properties": {
        "group": {
            "type": "string",
            "description": "id of the group to create the mapping for"},
        "groupName": {
            "type": "string",
            "description": "the name of the group"},
        "connectionName": {
            "type": "string",
            "pattern": "[a-zA-Z0-9-]*",
            "description": "the name of the connection to map"}
    }
}


class Auth0Exception(Exception, object):

    def __init__(self, msg):
        super(Auth0Exception, self).__init__(msg)


class Authz0GroupMappingProvider(Auth0Provider, object):

    def __init__(self):
        super(Authz0GroupMappingProvider, self).__init__()
        self.request_schema = request_schema

    @property
    def audience(self):
        return 'urn:auth0-authz-api'

    def is_supported_resource_type(self):
        return self.resource_type == 'Custom::Authz0GroupMapping'

    def get_group_mapping_url(self, group_id=None):
        if group_id is None:
            group_id = self.group_id
        return '{s.authz_url}/api/groups/{group_id}/mappings'.format(s=self, group_id=group_id)

    @property
    def group_id(self):
        return self.get('Value', {}).get('group', None)

    @property
    def mapping(self):
        return {name: self.get('Value')[name] for name in ['groupName', 'connectionName']}

    def matching_mapping(self, v):
        """
        returns true of the self.mapping is equal to v. The silly
        API of Auth0 Authorization extensions returns a connectionName in the form
        <name> (<type>) instead of <name>.

        :param v: the group mapping to compare
        :return:  true if self.mapping is equal to v
        """
        value_match = re.match(r'^(?P<name>[\w-]*)(\s\([^)]*\))?$', v['connectionName'])
        return self.mapping['groupName'] == v['groupName'] and \
            value_match is not None and \
            value_match.group('name') == self.mapping['connectionName']

    def get_group_mapping_id(self):
        """
        retrieves the id of the group mapping, or None if it does not exist.

        If a http status other than 200 or 404 is received, an Auth0Exception is raised.
        """

        self.add_authorization_header()
        r = requests.get(self.get_group_mapping_url(), headers=self.headers)
        if r.status_code == 200:
            result = next(filter(lambda m: self.matching_mapping(m), r.json()), None)
            return result['_id'] if result is not None else None
        elif r.status_code == 404:
            return None
        else:
            raise Auth0Exception(
                'failed to retrieve mapping for group id {s.group_id}, {r.status_code}, {r.text}'.format(
                    s=self, r=r))

    def patch(self):
        self.add_authorization_header()

        try:
            r = requests.patch(self.get_group_mapping_url(), headers=self.headers, json=[self.mapping])
            if r.status_code == 200 or r.status_code == 204 or r.status_code == 201:
                self.physical_resource_id = self.get_group_mapping_id()
                assert self.physical_resource_id is not None
            else:
                self.fail('patch failed with {r.status_code}, {r.text}'.format(r=r))
        except Auth0Exception as e:
            self.fail(str(e))

    def create(self):
        self.physical_resource_id = 'could-not-create'
        try:
            mapping_id = self.get_group_mapping_id()
            if mapping_id is None:
                self.patch()
            else:
                self.fail('already exists')
        except Auth0Exception as e:
            self.fail(str(e))

    def update(self):
        self.patch()

    def delete(self):
        if self.physical_resource_id == 'could-not-create':
            return

        self.add_authorization_header()
        r = requests.delete(self.get_group_mapping_url(), headers=self.headers, json=[self.physical_resource_id])
        if r.status_code != 200 and r.status_code != 204 and r.status_code != 404:
            self.fail('delete failed with code {r.status_code}, {r.text}'.format(r=r))


provider = Authz0GroupMappingProvider()


def handler(request, context):
    return provider.handle(request, context)
