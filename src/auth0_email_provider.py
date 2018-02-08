import re
import json
import requests

from auth0_provider import Auth0Provider

class Auth0EmailProviderProvider(Auth0Provider, object):
    """
    The Auth0 Emails Provider resource is different from other Auth0 resources:
    - it does not have an id.
    - a delete is not possible
    """
    def __init__(self):
        super(Auth0EmailProviderProvider, self).__init__()

    def is_supported_resource_type(self):
        return self.resource_type == 'Custom::Auth0EmailProvider'

    @property
    def auth0_resource_name(self):
        return 'emails/provider'

    def set_attributes_from_returned_value(self, value):
        self.physical_resource_id = value['name']

    def create(self):
        self.physical_resource_id = 'could-not-create'

        self.add_authorization_header()
        response = requests.post(self.url, headers=self.headers, json=self.get('Value'))
        if response.status_code in [200, 201]:
            self.set_attributes_from_returned_value(response.json())
        else:
            self.fail(response.text)

    def update(self):
        self.add_authorization_header()
        x = json.dumps(self.get('Value'))
        response = requests.patch(self.url, headers=self.headers, json=self.get('Value'))
        if response.status_code != 200:
            self.fail(response.text)

    def delete(self):
        if self.physical_resource_id == 'could-not-create':
            return

        self.add_authorization_header()
        response = requests.delete(self.url, headers=self.headers)
        if response.status_code not in [200, 204, 404]:
            self.fail(response.text)


provider = Auth0EmailProviderProvider()


def handler(request, context):
    return provider.handle(request, context)
