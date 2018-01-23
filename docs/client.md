## How do I deploy an Auth0 Client?
It is quite easy: you specify a CloudFormation resource of type `Custom::Auth0Client`.

```yaml
  Client:
    Type: Custom::Auth0Client
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        name: cfn-auth0-petstore-client
        description: Sample Auth0 Client
        app_type: non_interactive
        allowed_origins:
          - http://localhost:3000
        callbacks:
          - http://localhost:3000/consumer-api/v1/callback
```
In the `Value` you can specify all of the properties for the [Create a client](https://auth0.com/docs/api/management/v2#!/Clients/get_clients) operation.

After the deployment, the client `cfn-auth0-petstore-client` can be found in your Auth0 tenant. The client id
can be obtained through `!GetAtt 'Client.ClientId'`.

## Return values
For the Custom::Auth0Client the following values are available with 'Fn::GetAtt':

     `Domain` - the domain name of the application
     `ClientId` - the client id of the application

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

