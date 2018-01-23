# Custom::Auth0 resource provider
The `Custom::Auth0` resource provider for the standard Auth0 resources from the [Auth0 Management API](https://auth0.com/docs/api/management/v2).

## Syntax
To create a Auth0 resource using your your AWS CloudFormation template, use the following syntax:

```yaml
  Client:
    Type: Custom::Auth0<ResourceType> 
    Properties:
      Value:
        ### value as defined by the [Auth0 API](https://auth0.com/docs/api/management/v2)

      Connection:
        DomainParameterName: '/cfn-auth0-provider/domain'
        ClientIdParameterName: '/cfn-auth0-provider/client_id'
        ClientSecretParameterName: '/cfn-auth0-provider/client_secret'
        ClientSecretParameterName: '/cfn-auth0-provider/client_secret'

      OutputParameters:
        - Name: <parameter store parameter name>
          Path: <path into json response>
          Description: <of the parameter>

      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
```

## Supported Types
Supported Auth0 resource types are:

- clients - [Custom::Auth0Client](client.md)
- APIs - [Custom::Auth0ResourceProvider](resource-provider.md)
- client grants - [Custom::Auth0ClientGrant](client-grant.md)
- rules - [Custom::Auth0Rule](rule.md)
- connections - [Custom::Auth0Connection](connection.md)
- users - [Custom::Auth0User](user.md)

## Connection
In order to be able to manage the Auth0 credentials, you need to create an Non-Interactive application
in Auth0 which is granted to required permissions on the Auth0 Management API. 

By default, the credentials of this application should be stored in the 
[Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html) under 
`/cfn-auth0-provider/domain`, `/cfn-auth0-provider/client_id` and `/cfn-auth0-provider/client_secret`
respectively. The API endpoint of the Authorization extension should be stored under `/cfn-auth0-provider/authorization_url`.

```
aws ssm put-parameter --name /cfn-auth0-provider/domain --type String --value=$TENANT
aws ssm put-parameter --name /cfn-auth0-provider/client_id --type String --value=$CLIENT_ID
aws ssm put-parameter --name /cfn-auth0-provider/client_secret --type SecureString --value=$CLIENT_SECRET
aws ssm put-parameter --name /cfn-auth0-provider/authorization_url --type String --value="$AUTHORIZATION_URL`
```

If you store these credentials in a different location, please specify the correct parameter names.


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

## Value
You can specify the property for the specified resource:

    `Value` - All the attributes allowed from the [Auth0 API](https://auth0.com/docs/api/management/v2)

