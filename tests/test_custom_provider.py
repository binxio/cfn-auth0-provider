import uuid
import json
from provider import handler


sample_client = {
    "is_token_endpoint_ip_header_trusted": False,
    "name": "consumer-api",
    "is_first_party": True,
    "oidc_conformant": True,
    "sso_disabled": False,
    "cross_origin_auth": False,
    "description": "",
    "logo_uri": "",
    "sso": True,
    "callbacks": [
        "http://localhost:3000/consumer-api/v1/callback",
        "https://dev-api.coin.nl/consumerapi/v1/callback",
        "http://localhost:5000/consumer-api/v1/callback"
    ],
    "allowed_logout_urls": [],
    "allowed_clients": [],
    "allowed_origins": [
        "http://localhost:3000",
        "https://mvanholsteijn.eu.auth0.com/authorize",
        "https://mvanholsteijn.eu.auth0.com/login",
        "https://mvanholsteijn.eu.auth0.com"
    ],
    "jwt_configuration": {
        "alg": "RS256",
        "lifetime_in_seconds": 3600
    },
    "token_endpoint_auth_method": "none",
    "app_type": "spa",
    "grant_types": [
        "authorization_code",
        "http://auth0.com/oauth/grant-type/password-realm",
        "implicit",
        "password",
        "refresh_token"
    ],
    "custom_login_page_on": True
}


def test_create():
    # create
    client = json.loads(json.dumps(sample_client))
    client['name'] = 'n%s' % uuid.uuid4()
    request = Request('Create', client)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    assert 'ClientId' in response['Data']
    assert response['PhysicalResourceId'] == response['Data']['ClientId']

    # update
    request = Request('Update', client, response['PhysicalResourceId'])
    response = handler(request, {})
    print json.dumps(response, indent=2)
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response
    assert 'ClientId' in response['Data']
    assert response['PhysicalResourceId'] == response['Data']['ClientId']

    # delete
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', {}, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']


class Request(dict):

    def __init__(self, request_type, value, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::Auth0Client',
            'LogicalResourceId': 'MyCustom',
            'ResourceProperties': {
                'Value': value
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
