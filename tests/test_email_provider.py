import json
import uuid
from provider import handler

sample_provider = {
        "name": "smtp",
        "enabled": True,
        "default_from_address": "no-reply@me.com",
        "credentials": {
            "smtp_host": "email-smtp.eu-central-1.amazonaws.com",
            "smtp_port": 587,
            "smtp_user": "pipo",
            "smtp_pass": "password"
        },
        "settings": {}
}


def test_create():
    # create
    value = json.loads(json.dumps(sample_provider))
    request = Request('Create', value)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response

    request = Request('Create', value)
    response = handler(request, {})
    assert response['Status'] == 'FAILED', response['Reason']
    assert 'PhysicalResourceId' in response
    assert len(response['Reason']) > 0
    assert response['PhysicalResourceId'] == 'could-not-create'

    # update
    value['credentials']['smtp_host'] = 'another-localhost'
    request = Request('Update', value, response['PhysicalResourceId'])
    response = handler(request, {})
    print(json.dumps(response, indent=2))
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert 'PhysicalResourceId' in response

    # delete
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', {}, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete again
    request = Request('Delete', {}, physical_resource_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete incorrect physical resource id
    request = Request('Delete', {}, 'devapi-consumeradmin-ManageOwnConsumersPermission-Y38O818GY2PV')
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
            'ResourceType': 'Custom::Auth0EmailProvider',
            'LogicalResourceId': 'MyCustomEmailProvider',
            'ResourceProperties': {
                'Value': value
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
