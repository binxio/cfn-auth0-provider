import re
import boto3
import requests
import logging
from cfn_resource_provider import ResourceProvider
from auth0_access_token import get_access_token

#
# The request schema defining the Resource Properties
#
request_schema = {
    "type": "object",
    "required": ["Value"],
    "properties": {
        "Connection": {
            "type": "object",
            "required": ["TenantParameterName", "ClientIdParameterName",  "ClientSecretParameterName"],
            "properties": {
                "TenantParameterName": {
                    "type": "string",
                    "default": "/cfn-auth0-provider/tenant",
                    "description": "Name of the parameter in the Parameter Store with the Auth0  tenant"},
                "ClientIdParameterName": {
                    "type": "string",
                    "default": "/cfn-auth0-provider/client_id",
                    "description": "Name of the parameter in the Parameter Store for the Client id"},
                "ClientSecretParameterName": {
                    "type": "string",
                    "default": "/cfn-auth0-provider/client_secret",
                    "description": "Name of the parameter in the Parameter Store for the Client secret"}
            }
        },
        "Value": {
            "type": "object",
            "description": "values for this resource"
        }
    }
}

log = logging.getLogger(name=__name__)


class Auth0Provider(ResourceProvider):
    """
    Generic Cloudformation custom resource provider for Auth0 resources.
    """

    def __init__(self):
        super(Auth0Provider, self).__init__()
        self.request_schema = request_schema
        self.ssm = boto3.client('ssm')

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    def get_ssm_parameter(self, name):
        v = self.ssm.get_parameter(Name=name, WithDecryption=True)
        return v['Parameter']['Value']

    def get_token(self):
        c = self.get(
            'Connection',
            {"TenantParameterName": "/cfn-auth0-provider/tenant",
             "ClientIdParameterName": "/cfn-auth0-provider/client_id",
             "ClientSecretParameterName": "/cfn-auth0-provider/client_secret"})

        self.tenant = self.get_ssm_parameter(c.get('TenantParameterName'))
        self.tenant = self.tenant[:-1] if self.tenant.endswith('/') else self.tenant
        if not self.tenant.startswith('http'):
            self.tenant = 'https://%s' % self.tenant

        self.client_id = self.get_ssm_parameter(c.get('ClientIdParameterName'))
        self.client_secret = self.get_ssm_parameter(c.get('ClientSecretParameterName'))
        self.access_token = get_access_token(self.tenant, self.client_id, self.client_secret)
        self.headers = {'Authorization': 'Bearer %s' % self.access_token}

    def is_supported_resource_type(self):
        print '>>> is_supported_resource_type() = %s, %s' % (self.resource_type.startswith('Custom::Auth0'), self.request_type)
        return self.resource_type.startswith('Custom::Auth0')

    @property
    def uri(self):
        """
        converts the uri associated with the resource type specified.
        Auth0Client -> /api/v2/clients
        Auth0ClientGrant -> /api/v2/client-grants
        Auth0Connection -> /api/v2/connections
        ...
        """
        name = self.resource_type.replace('Custom::Auth0', '')
        return '/api/v2/%s%ss' % (name[0].lower(), re.sub(r'([A-Z])', lambda p: '-%s' % p.group(1).lower(), name[1:]))

    @property
    def url(self):
        return '%s%s' % (self.tenant, self.uri)

    def set_attributes_from_returned_value(self, value):
        """
        callback to set additional attributes from returned value to be accessed through Fn::GetAtt.
        """
        pass

    def set_physical_resource_id_from_value(self, value):
        # ugly hack: the API of Auth0 returns the id as the property 'id' for all resource types, except for Clients...
        self.physical_resource_id = value['id'] if self.resource_type != 'Custom::Auth0Client' else value['client_id']
        

    def create(self):
        self.get_token()
        print self.url
        r = requests.post(self.url, headers=self.headers, json=self.get('Value'))
        if r.status_code == 201:
            value = r.json()
            self.set_physical_resource_id_from_value(value)
            self.set_attributes_from_returned_value(value)
        else:
            self.physical_resource_id = 'could-not-create'
            self.fail('status code %d, %s' % (r.status_code, r.text))

    def update(self):
        self.get_token()
        r = requests.patch('%s/%s' % (self.url, self.physical_resource_id),
                           headers=self.headers, json=self.get('Value'))
        if r.status_code == 200:
            value = r.json()
            self.set_physical_resource_id_from_value(value)
            self.set_attributes_from_returned_value(value)
        else:
            self.fail('status code %d, %s' % (r.status_code, r.text))

    def delete(self):
        self.get_token()
        r = requests.delete('%s/%s' % (self.url, self.physical_resource_id), headers=self.headers)
        if r.status_code != 204:
            self.fail('status code %d, %s' % (r.status_code, r.text))

provider = Auth0Provider()


def handler(request, context):
    return provider.handle(request, context)
