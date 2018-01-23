## How do I create an Auth0 permission?
You specify a CloudFormation resource of type `Custom::Authz0Permission`.

```yaml
  CreatePermission:
    Type: Custom::Authz0Permission
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        applicationType: client
        applicationId: !Ref Client
        description: "create pets"
        name: "create:pets"
```

In the `Value` you can specify all of the properties for the [Create a permission](https://auth0.com/docs/api/authorization-extension#create-permission) operation.


