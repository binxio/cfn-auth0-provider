import uuid
import json
from provider import handler
import boto3
from botocore.exceptions import ClientError


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


def test_output_parameters():
    name = 'n%s' % uuid.uuid4()
    outputs = [
        {
            'Path': 'client_id',
            'Name': '/cfn-auth0-provider/clients/%s/client_id' % name,
            'Description': 'my client id'},
        {
            'Path': 'client_secret',
            'Name': '/cfn-auth0-provider/clients/%s/client_secret' % name}
    ]
    # create
    client = json.loads(json.dumps(sample_client))
    client['name'] = name
    request = Request('Create', client)
    request['ResourceProperties']['OutputParameters'] = outputs
    response = handler(request, {})

    assert response['Status'] == 'SUCCESS', response['Reason']
    client_id = response['PhysicalResourceId']

    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(Name=outputs[0]['Name'], WithDecryption=True)

    assert parameter['Parameter']['Value'] == client_id

    filter = {
        'Key': 'Name',
        'Values': [outputs[0]['Name']]
    }
    parameters = ssm.describe_parameters(Filters=[filter])
    assert parameters['Parameters'][0]['Description'] == outputs[0]['Description']

    # check the client secret is stored..
    parameter = ssm.get_parameter(Name=outputs[1]['Name'], WithDecryption=True)

    # update
    new_outputs = [{
        'Path': 'client_id',
        'Name': '/cfn-auth0-provider/clients/%s/client_secret' % name}
    ]

    request = Request('Update', client, response['PhysicalResourceId'])
    request['OldResourceProperties'] = {}
    request['OldResourceProperties']['OutputParameters'] = outputs
    request['ResourceProperties']['OutputParameters'] = new_outputs
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # check the client_id was written in the secret parameter
    parameter = ssm.get_parameter(Name=new_outputs[0]['Name'], WithDecryption=True)
    assert parameter['Parameter']['Value'] == client_id
    # check that the removed output is deleted.
    try:
        parameter = ssm.get_parameter(Name=outputs[0]['Name'], WithDecryption=True)
        assert False, '%s should not exist' % parameter['Parameter']['Name']
    except ClientError as e:
        assert e.response['Error']['Code'] == 'ParameterNotFound'

    # delete
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', {}, physical_resource_id)
    request['ResourceProperties']['OutputParameters'] = outputs
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    for parameter in outputs:
        try:
            parameter = ssm.get_parameter(Name=parameter['Name'], WithDecryption=True)
            assert False, '%s should not exist' % parameter['Name']
        except ClientError as e:
            assert e.response['Error']['Code'] == 'ParameterNotFound'


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
