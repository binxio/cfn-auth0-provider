import uuid
import json
from provider import handler
import boto3
import logging

logging.getLogger('boto3').setLevel(logging.CRITICAL)

ssm = boto3.client('ssm')


def get_parameter(name):
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']


def test_create_group():
    # create
    name = 'n%s' % uuid.uuid4()
    group = {'name': name, 'description': 'group of {}'.format(name)}
    request = Request('Create', group)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response

    # duplicate create should fail...
    err_response = handler(request, {})
    assert err_response['Status'] == 'FAILED'

    # update
    group['description'] = 'groep van {}'.format(name)
    request = Request('Update', group, response['PhysicalResourceId'])
    response = handler(request, {})
    print(json.dumps(response, indent=2))
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response

    # delete
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', {}, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # duplicate delete is ok...
    err_response = handler(request, {})
    assert err_response['Status'] == 'SUCCESS'


class Request(dict):

    def __init__(self, request_type, value, physical_resource_id=None):
        super(Request, self).__init__()
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::Authz0Group',
            'LogicalResourceId': 'MyCustomGroup',
            'ResourceProperties': {
                'Value': value
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
