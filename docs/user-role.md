## How do I assign a role to a user?
You specify a CloudFormation resource of type `Custom::Authz0UserRole`.

```yaml
  CustomerUserRole:
    Type: Custom::Authz0UserRole
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        user: !Ref CustomerUser
        role: !Ref CustomerRole
```

In the `Value` you specify the ids of the [user](user.md) and [role](role.md) you want to assign.
