import re
import json
import boto3
import requests
import logging
from botocore.exceptions import ClientError
from cfn_resource_provider import ResourceProvider
from auth0_access_token import get_access_token
from request_update import create_update_request, get_property_value_by_path

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
        "OutputParameters": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["Name", "Path"],
                "properties": {
                    "Name": {
                        "type": "string",
                        "description": "name of the parameter to store the value in"},
                    "Path": {
                        "type": "string",
                        "description": "path to the value to be stored, seperated with ."},
                    "Description": {
                        "type": "string",
                        "default": "",
                        "description": "for the value in the parameter store"},
                    "KeyAlias": {
                        "type": "string",
                        "default": "alias/aws/ssm",
                        "description": "KMS key alias to use to encrypt the value"}
                }
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
        print json.dumps(value, indent=2)
        """
        callback to set additional attributes from returned value to be accessed through Fn::GetAtt.
        """
        if self.resource_type == 'Custom::Auth0Client':
            self.physical_resource_id = value['client_id']
            self.set_attribute('Tenant', value['tenant'])
            self.set_attribute('ClientId', value['client_id'])
        else:
            self.physical_resource_id = value['id']

    def create(self):
        self.get_token()
        print self.url
        r = requests.post(self.url, headers=self.headers, json=self.get('Value'))
        if r.status_code == 201:
            self.set_attributes_from_returned_value(r.json())
            self.store_output_parameters(r.json(), overwrite=False)
        else:
            self.physical_resource_id = 'could-not-create'
            self.fail('status code %d, %s' % (r.status_code, r.text))

    def update(self):
        self.get_token()
        value = create_update_request(self.resource_type, self.get_old('Value'), self.get('Value'))
        r = requests.patch('%s/%s' % (self.url, self.physical_resource_id), headers=self.headers, json=value)
        if r.status_code == 200:
            self.set_attributes_from_returned_value(r.json())
            self.store_output_parameters(r.json(), overwrite=True)
            self.remove_deleted_parameters()
        else:
            self.fail('status code %d, %s' % (r.status_code, r.text))

    def remove_deleted_parameters(self):
        old_parameters = set(map(lambda p: p['Name'], self.get_old('OutputParameters', [])))
        current_parameters = set(map(lambda p: p['Name'], self.get('OutputParameters', [])))
        to_delete = old_parameters - current_parameters
        for name in to_delete:
            try:
                self.ssm.delete_parameter(Name=name)
            except ClientError as e:
                if e.response['Error']['Code'] != 'ParameterNotFound':
                    log.warn('failed to delete "%s" from parameter store, %s', name, str(e))

    def delete(self):
        if self.physical_resource_id != 'could-not-create':
            self.get_token()
            r = requests.delete('%s/%s' % (self.url, self.physical_resource_id), headers=self.headers)
            if r.status_code == 204:
                self.delete_output_parameters()
            else:
                self.fail('status code %d, %s' % (r.status_code, r.text))
        else:
            pass  # object was not created in the first place

    def delete_output_parameters(self):
        parameters = self.get('OutputParameters', [])
        for name in map(lambda p: p['Name'], parameters):
            try:
                self.ssm.delete_parameter(Name=name)
            except ClientError as e:
                if e.response['Error']['Code'] != 'ParameterNotFound':
                    log.warn('failed to delete "%s" from parameter store, %s', name, str(e))

    def store_output_parameters(self, obj, overwrite=False):
        parameters = self.get('OutputParameters', [])
        for parameter in parameters:
            path = parameter['Path']
            name = parameter['Name']
            value = get_property_value_by_path(obj, path)
            if value is not None:
                try:
                    kwargs = {
                        'Name': name,
                        'Type': 'SecureString',
                        'Value': value,
                        'Overwrite': overwrite
                    }
                    if 'Description' in parameter:
                        kwargs['Description'] = parameter['Description']
                    if 'KeyAlias' in parameter:
                        kwargs['KeyId'] = parameter['KeyAlias']

                    self.ssm.put_parameter(**kwargs)
                except ClientError as e:
                    self.fail(str(e))
            else:
                self.fail('path %s did not result in a value' % path)


provider = Auth0Provider()


def handler(request, context):
    return provider.handle(request, context)
