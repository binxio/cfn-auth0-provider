import json
import requests
import base64
from past.builtins import basestring

from auth0_provider import Auth0Provider


class AuthzAssociationProvider(Auth0Provider, object):
    """
    """

    def __init__(self, supported_resource_type, owner, owned, collection=None):
        super(AuthzAssociationProvider, self).__init__()
        self.supported_resource_type = supported_resource_type
        self.owner = owner
        self.owned = owned
        self.collection = collection if collection is not None else '{}s'.format(owned)

    @property
    def audience(self):
        return 'urn:auth0-authz-api'

    def is_supported_resource_type(self):
        return self.resource_type == self.supported_resource_type

    def get_id(self, name):
        value = self.get('Value')
        if name in value and isinstance(value[name], basestring):
            return value[name]
        else:
            return None

    @property
    def owner_id(self):
        return self.get_id(self.owner)

    @property
    def owned_id(self):
        return self.get_id(self.owned)

    def is_valid_request(self):
        if super(AuthzAssociationProvider, self).is_valid_request():
            if self.request_type == 'Create' or self.request_type == 'Update':
                value = self.get('Value')
                if self.owner_id is None:
                    self.fail('missing property "{s.owner}" or not a string.'.format(s=self))
                    return False
                if self.owned_id is None:
                    self.fail('missing property "{s.owned}" or not a string.'.format(s=self))
                    return False
            return True
        else:
            return False

    def get_owner_url(self, owner_id=None):
        if owner_id is None:
            owner_id = self.owner_id
        return '{s.authz_url}/api/{s.owner}s/{owner_id}/{s.collection}'.format(s=self, owner_id=owner_id)

    def encode_physical_resource_id(self):
        v = json.dumps([self.owner_id, self.owned_id], ensure_ascii=False).encode("utf8")
        self.physical_resource_id = base64.b64encode(v).decode('ascii')

    def decode_physical_resource_id(self):
        owner_id, owned_id = json.loads(base64.b64decode(self.physical_resource_id))
        return owner_id, owned_id

    def create_or_update(self):
        self.add_authorization_header()

        r = requests.patch(self.get_owner_url(), headers=self.headers, json=[self.owned_id])
        if r.status_code == 200 or r.status_code == 204 or r.status_code == 201:
            self.encode_physical_resource_id()
        else:
            self.fail('create {s.owner} failed with code {r.status_code}, {r.text}'.format(s=self, r=r))

    def create(self):
        self.create_or_update()
        if self.status == 'FAILED':
            self.physical_resource_id = 'could-not-create'

    def update(self):
        self.create_or_update()

    def delete(self):
        if self.physical_resource_id == 'could-not-create':
            return

        self.add_authorization_header()
        owner_id, owned_id = self.decode_physical_resource_id()

        r = requests.delete(self.get_owner_url(owner_id), headers=self.headers, json=[owned_id])
        if r.status_code != 200 and r.status_code != 204:
            self.fail('delete failed with code {r.status_code}, {r.text}'.format(r=r))
