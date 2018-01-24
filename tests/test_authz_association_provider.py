import uuid
import time
from provider import handler
import boto3


ssm = boto3.client('ssm')


def get_parameter(name):
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']


def test_all_stuff():
    # create client
    name = 'test-%s' % uuid.uuid4()
    clinet = {'name': name}
    request = Request('Create', 'Custom::Auth0Client', client)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    client_id = response['PhysicalResourceId']

    # create api
    api = {'name': name, 'identifier': 'urn:' + name}
    request = Request('Create', 'Custom::Auth0ResourceServer', api)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    api_id = response['PhysicalResourceId']

    # create permission
    permission = {'name': 'test-update:pets', 'description': 'update pets', 'applicationId': client_id, 'applicationType': 'client'}
    request = Request('Create', 'Custom::Authz0Permission', permission)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    permission_id = response['PhysicalResourceId']

    # create role
    role = {'name': name, 'description': 'role of {}'.format(
        name),  'applicationId': client_id, 'applicationType': 'client', 'permissions': [permission_id]}
    request = Request('Create', 'Custom::Authz0Role', role)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    role_id = response['PhysicalResourceId']

    # create client
    client = {'name': name}
    request = Request('Create', 'Custom::Auth0Client', client)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    client_id = response['PhysicalResourceId']

    # create connection
    connection_name = 'test-{}'.format(name.replace('-', '')[5:20])
    connection = {'name': connection_name, 'strategy': 'auth0', 'enabled_clients': [
        get_parameter('/cfn-auth0-provider/client_id'), client_id]}
    request = Request('Create', 'Custom::Auth0Connection', connection)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    connection_id = response['PhysicalResourceId']
    time.sleep(0.5)

    # create user
    user = {'name': name, 'connection': connection_name, 'email': '{}@auth0.local'.format(name),
            'password': name}
    request = Request('Create', 'Custom::Auth0User', user)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    user_id = response['PhysicalResourceId']

    # grant role to user
    user_role = {'user': user_id, 'role': role_id}
    request = Request('Create', 'Custom::Authz0UserRole', user_role)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    user_role_id = response['PhysicalResourceId']

    # create group
    group = {'name': name, 'description': 'group of {}'.format(name)}
    request = Request('Create', 'Custom::Authz0Group', group)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    group_id = response['PhysicalResourceId']

    # create group 2
    group = {'name': name + '-2', 'description': 'second group of {}'.format(name)}
    request = Request('Create', 'Custom::Authz0Group', group)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    group2_id = response['PhysicalResourceId']

    # add user (member) to group
    group_member = {'group': group_id, 'member': user_id}
    request = Request('Create', 'Custom::Authz0GroupMember', group_member)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    group_member_id = response['PhysicalResourceId']

    # grant role to group
    group_role = {'group': group_id, 'role': role_id}
    request = Request('Create', 'Custom::Authz0GroupRole', group_role)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    group_role_id = response['PhysicalResourceId']

    # assigned group to group
    assignment = {'group': group_id, 'nested': group2_id}
    print (assignment)
    request = Request('Create', 'Custom::Authz0GroupNested', assignment)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    nested_group_id = response['PhysicalResourceId']

    # create group mapping
    group_mapping_request = {'group': group_id, 'groupName': 'googlers', 'connectionName': 'google-oauth2'}
    request = Request('Create', 'Custom::Authz0GroupMapping', group_mapping_request)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    group_mapping_id = response['PhysicalResourceId']

    # update group mapping
    group_mapping_request = {'group': group_id, 'groupName': 'googelaars', 'connectionName': 'google-oauth2'}
    request = Request('Update', 'Custom::Authz0GroupMapping', group_mapping_request, physical_resource_id=group_mapping_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']
    group_mapping_id_2 = response['PhysicalResourceId']
    assert group_mapping_id != group_mapping_id_2

    # delete group to group
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', 'Custom::Authz0GroupNested', {}, nested_group_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete group mapping 1
    group_mapping_request = {'group': group_id, 'groupName': 'googelaars', 'connectionName': 'google-oauth2'}
    request = Request('Delete', 'Custom::Authz0GroupMapping', group_mapping_request, physical_resource_id=group_mapping_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete group mapping 2
    group_mapping_request = {'group': group_id, 'groupName': 'googelaars', 'connectionName': 'google-oauth2'}
    request = Request('Delete', 'Custom::Authz0GroupMapping', group_mapping_request, physical_resource_id=group_mapping_id_2)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete group2
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', 'Custom::Authz0Group', {}, group2_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete group
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', 'Custom::Authz0Group', {}, group_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete role
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', 'Custom::Authz0Role', {}, role_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete permission
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', 'Custom::Authz0Permission', {}, permission_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete api
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', 'Custom::Auth0ResourceServer', {}, api_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']

    # delete client
    physical_resource_id = response['PhysicalResourceId']
    request = Request('Delete', 'Custom::Auth0Client', {}, client_id)
    response = handler(request, {})
    assert response['Status'] == 'SUCCESS', response['Reason']


class Request(dict):

    def __init__(self, request_type, resource_type, value, physical_resource_id=None):
        super(Request, self).__init__()
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': resource_type,
            'LogicalResourceId': 'MyCustomGroup',
            'ResourceProperties': {
                'Value': value
            }})

        self['PhysicalResourceId'] = physical_resource_id if physical_resource_id is not None else 'initial-%s' % str(uuid.uuid4())
