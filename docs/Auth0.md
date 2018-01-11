# Custom::Auth0 resource provider
The `Custom::Auth0` resource provider.

## Syntax
To create a Auth0 resource using your your AWS CloudFormation template, use the following syntax:

```yaml
  Client:
    Type: Custom::Auth0<ResourceType>
    Properties:
      Value:
        ### value as defined by the [Auth0 API](https://auth0.com/docs/api/management/v2)

      Connection:
	TenantParameterName: '/cfn-auth0-provider/tenant'
	ClientIdParameterName: '/cfn-auth0-provider/client_id'
	ClientSecretParameterName: '/cfn-auth0-provider/client_secret'

      OutputParameters:
	- Name: /cfn-auth0-provider/resource/id
	  Path: id
          Description: Id of the created resource

      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
```

## Supported Auth0 Types
Supported Auth0 resource types are:

	- clients - Custom::Auth0Client
	- APIs - Custom::Auth0ResourceProviders 
	- client grants - Custom::Auth0ClientGrant 
	- rules - Custom::Auth0Rules 

In principle any Auth0 resource which supports a POST, PATCH and DELETE can be managed. Please make sure that
your non-interactive client has the appropriate privileges.

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
`/cfn-auth0-provider/tenant`, `/cfn-auth0-provider/client_id` and `/cfn-auth0-provider/client_secret`
respectively.

```
   aws ssm put-parameter --name /cfn-auth0-provider/tenant --type SecureString --value=$TENANT
   aws ssm put-parameter --name /cfn-auth0-provider/client\_id --type SecureString --value=$CLIENT\_ID
   aws ssm put-parameter --name /cfn-auth0-provider/client\_secret --type SecureString --value=$CLIENT\_SECRET
```

If you store these credentials in a different location, please specify the correct parameter names.


## Properties
You can specify the following properties:

    `Value` - All the attributes allowed from the [Auth0 API](https://auth0.com/docs/api/management/v2)

## Return values
For the Custom::Auth0Client the following values are available with 'Fn::GetAtt':

     `Tenant` - the tenant name of the application
     `ClientId` - the client id of the application

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

