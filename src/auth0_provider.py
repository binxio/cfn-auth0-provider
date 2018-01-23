import re
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
            "required": ["TenantParameterName", "ClientIdParameterName", "ClientSecretParameterName"],
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
                    "description": "Name of the parameter in the Parameter Store for the Client secret"},
                "AuthorizationExtensionUrlParameterName": {
                    "type": "string",
                    "default": "/cfn-auth0-provider/authorization_url",
                    "description": "Name of the parameter in the Parameter Store for the Authorization extension URL"}
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


class Auth0Provider(ResourceProvider, object):
    """
    Generic Cloudformation custom resource provider for Auth0 resources.
    """

    def __init__(self):
        super(Auth0Provider, self).__init__()
        self.request_schema = request_schema
        self.ssm = boto3.client('ssm')
        self._connection_info = None
        self.headers = {}

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    def get_ssm_parameter(self, name):
        value = self.ssm.get_parameter(Name=name, WithDecryption=True)
        return value['Parameter']['Value']

    @property
    def connection_info(self):
        if not self._connection_info:
            self._connection_info = self.get(
                'Connection',
                {"DomainParameterName": "/cfn-auth0-provider/domain",
                 "ClientIdParameterName": "/cfn-auth0-provider/client_id",
                 "ClientSecretParameterName": "/cfn-auth0-provider/client_secret",
                 "AuthorizationExtensionUrlParameterName": "/cfn-auth0-provider/authorization_url"})
        return self._connection_info

    @property
    def base_url(self):
        base_url = self.get_ssm_parameter(self.connection_info.get('DomainParameterName'))
        base_url = base_url[:-1] if base_url.endswith('/') else base_url
        if not base_url.startswith('http'):
            base_url = 'https://{}'.format(base_url)
        return base_url

    @property
    def client_id(self):
        return self.get_ssm_parameter(self.connection_info.get('ClientIdParameterName'))

    @property
    def client_secret(self):
        return self.get_ssm_parameter(self.connection_info.get('ClientSecretParameterName'))

    @property
    def authz_url(self):
        url = self.get_ssm_parameter(self.connection_info.get('AuthorizationExtensionUrlParameterName'))
        return url[:-1] if url.endswith('/') else url

    @property
    def audience(self):
        return '{}/api/v2/'.format(self.base_url)

    @property
    def access_token(self):
        return get_access_token(self.base_url, self.client_id, self.client_secret, self.audience)

    def add_authorization_header(self):
        self.headers = {'Authorization': 'Bearer {}'.format(self.access_token)}

    def is_supported_resource_type(self):
        return self.resource_type.startswith('Custom::Auth0')

    @property
    def auth0_resource_name(self):
        """
        converts the the custom resource name to the associated Auth0 resource
        Auth0Client -> clients
        Auth0ClientGrant -> client-grants
        Auth0Connection -> connections
        ...
        """
        name = re.sub(r'^Custom::Authz?0', '', self.resource_type)
        return '{}{}s'.format(name[0].lower(), re.sub(r'([A-Z])', lambda p: '-{}'.format(p.group(1).lower()), name[1:]))

    @property
    def url(self):
        return '{}/api/v2/{}'.format(self.base_url, self.auth0_resource_name)

    def set_attributes_from_returned_value(self, value):
        """
        callback to set additional attributes from returned value to be accessed through Fn::GetAtt.
        """
        if self.resource_type == 'Custom::Auth0Client':
            self.physical_resource_id = value['client_id']
            self.set_attribute('Tenant', value['tenant'])
            self.set_attribute('ClientId', value['client_id'])
        elif self.resource_type == 'Custom::Auth0User':
            self.physical_resource_id = value['user_id']
        else:
            self.physical_resource_id = value['id']

    def create(self):
        if self.check_parameters_precondition():
            self.add_authorization_header()
            r = requests.post(self.url, headers=self.headers, json=self.get('Value'))
            if r.status_code == 200 or r.status_code == 201:
                self.set_attributes_from_returned_value(r.json())
                self.store_output_parameters(r.json(), overwrite=False)
            else:
                self.physical_resource_id = 'could-not-create'
                self.fail('create failed with code {}, {}'.format(r.status_code, r.text))
        else:
            self.physical_resource_id = 'could-not-create'

    @property
    def rest_update_operation(self):
        return 'PATCH'

    def update(self):
        self.add_authorization_header()
        value = create_update_request(self.resource_type, self.get_old('Value'), self.get('Value'))
        request = requests.Request(
            self.rest_update_operation, '{}/{}'.format(self.url, self.physical_resource_id),
            headers=self.headers, json=value).prepare()
        r = (requests.Session()).send(request)
        if r.status_code == 200:
            self.set_attributes_from_returned_value(r.json())
            self.store_output_parameters(r.json(), overwrite=True)
            self.remove_deleted_parameters()
        else:
            self.fail('status code from {} on {}, {}, {}'.format(request.method, r.url, r.status_code, r.text))

    def check_parameters_precondition(self):
        names = list(map(lambda p: p['Name'], self.get('OutputParameters', [])))
        if len(names) > 0:
            try:
                r = self.ssm.describe_parameters(Filters=[{'Key': 'Name', 'Values': names}])
                if len(r['Parameters']) > 0:
                    self.fail('one or more of the parameters {} already exist'.format(names))
            except ClientError as e:
                self.fail('failed to determine the presence of output parameters, {}'.format(str(e)))
        return self.status == 'SUCCESS'

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
            self.add_authorization_header()
            r = requests.delete('{}/{}'.format(self.url, self.physical_resource_id), headers=self.headers)
            if r.status_code == 204:
                self.delete_output_parameters()
            else:
                self.fail('status code {}, {}'.format(r.status_code, r.text))
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
                self.fail('path {} did not result in a value'.format(path))


provider = Auth0Provider()


def handler(request, context):
    return provider.handle(request, context)
