# Custom::Authz0 resource provider
The `Custom::Authz0` resource provider for resources managed by the [Auth0 Authorization Extension API](https://auth0.com/docs/extensions/authorization-extension/v2).

## Syntax
To create an Auth0 Authorization extension resource using your your AWS CloudFormation template, use the following syntax:

```yaml
  Client:
    Type: Custom::Authz0<ResourceType>
    Properties:
      Value:
        ### value as defined by the [Auth0 Authorization Extension API](https://auth0.com/docs/api/authorization-extension)

      Connection:
        DomainParameterName: '/cfn-auth0-provider/domain'
        ClientIdParameterName: '/cfn-auth0-provider/client_id'
        ClientSecretParameterName: '/cfn-auth0-provider/client_secret'
        AuthorizationExtensionUrlParameterName: '/cfn-auth0-provider/authorization_url'

      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
```

## Supported Types

- permissions - [Custom::Authz0Permission](permission.md)
- roles - [Custom::Authz0Role](role.md)
- groups - [Custom::Authz0Group](group.md)
- group members - [Custom::Authz0GroupMember](group.md)
- group roles - [Custom::Authz0GroupRole](group.md)
- user roles - [Custom::Authz0UserRole](user-role.md)
- group mappings - [Custom::Authz0GroupMapping](group.md)
- nested groups - [Custom::Authz0GroupNested](group.md)

## Output Parameters
In order to copy credentials from created resources into the parameter store, you can specify `OutputParameters`:

- `Path` - to the required property from the created or updated object
- `Name` - of the value in the Parameter Store
- `Description` - of the value
- `KeyAlias` - Optional, key to use to encrypt the value

for example:

```
   OutputParameters:
     - Name: /auth0-resources/sample-client/client_id
       Path: client_id
       Description: client id of the sample client

     - Name: /auth0-resources/sample-client/client_secret
       Path: client_secret
       Description: client secret of the sample client
```

## Connection
In order to be able to manage the Auth0 credentials, you need to create an Non-Interactive application
in Auth0 which is granted to required permissions on the Auth0 Management API. 

By default, the credentials of this application should be stored in the 
[Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html) under 
`/cfn-auth0-provider/domain`, `/cfn-auth0-provider/client_id` and `/cfn-auth0-provider/client_secret`
respectively.

```
   aws ssm put-parameter --name /cfn-auth0-provider/domain --type String --value=$TENANT
   aws ssm put-parameter --name /cfn-auth0-provider/client_id --type String --value=$CLIENT_ID
   aws ssm put-parameter --name /cfn-auth0-provider/client_secret --type SecureString --value=$CLIENT_SECRET
   aws ssm put-parameter --name /cfn-auth0-provider/authorization_url --type String --value="$AUTHORIZATION_URL"
```

If you store these credentials in a different location, please specify the correct parameter names.


## Properties
You can specify the properties for the specified resource.

