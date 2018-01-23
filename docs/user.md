## How do I create an Auth0 user ?
You specify a CloudFormation resource of type `Custom::Auth0User`.

```yaml
  API:
    Type: Custom::Auth0User
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value: 
        connection: petstore
        email: customer@petstore.local
        password: secret
```

In the `Value` you can specify all of the properties for the [Create a user](https://auth0.com/docs/api/management/v2#!/Users/post_users) operation.
