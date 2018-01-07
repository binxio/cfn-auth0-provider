# Custom::Auth0Client
The `Custom::Auth0Client` provider.

## Syntax
To create a Auth0 Client in your AWS CloudFormation template, use the following syntax:

```yaml
  Client:
    Type: Custom::Auth0Client
    Properties:
      Value:
        name: cfn-auth0-petsstore-client
        description: Sample Auth0 Client
        app_type: non_interactive
        ...
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'

```

## Properties
You can specify the following properties:

    `Value` - All the attributes allowed from the [Auth0 API for Clients](https://auth0.com/docs/api/management/v2#!/Clients/post_clients)


## Return values
With 'Fn::GetAtt' the following values are available:

- `ClientId` - The id for the Auth0 Client
- `PublicKeyPEM` - the public key of the Auth0 client in PEM format

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).
