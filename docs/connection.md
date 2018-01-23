## How do I deploy an Auth0 Connection?
You specify a CloudFormation resource of type `Custom::Auth0Connection`.

```yaml
  API:
    Type: Custom::Auth0Connection
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value: 
        name: my-user-name-password
        strategy: auth0
        enabled_clients:
          - !Ref CustomCfnProviderClientId
          - !Ref Client
```
In the `Value` you can specify all of the properties for the [Create a connection](https://auth0.com/docs/api/management/v2#!/Connections/post_connections) operation.

If you wish the custom cloudformation provider to be able to add users, add the client id of the
provider to the enabled\_clients. See [Installation][#Installation].

