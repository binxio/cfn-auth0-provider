## How do I create an Auth0 role?
You specify a CloudFormation resource of type `Custom::Authz0Role`.

```yaml
  OwnerRole:
    Type: Custom::Authz0Role
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        applicationType: client
        applicationId: !Ref Client
        description: owner of the petstore
        name: petstore-owner
        permissions:
          - !Ref CreatePermission
          - !Ref UpdatePermission
          - !Ref DeletePermission
          - !Ref GetPermission
```

In the `Value` you can specify all of the properties for the [Create a role](https://auth0.com/docs/api/authorization-extension#create-role) operation.

