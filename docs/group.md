## How do I create an Auth0 group?
You specify a CloudFormation resource of type `Custom::Authz0Group`.

```yaml
  CustomerGroup:
    Type: Custom::Authz0Group
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        description: group of customers of the petstore
        name: petstore-customers
```

In the `Value` you can specify all of the properties for the [Create a group](https://auth0.com/docs/api/authorization-extension#create-group) operation.

## How do I nest a group?
You specify a CloudFormation resource of type `Custom::Authz0GroupNested`.

```yaml
  GroupNested:
    Type: Custom::Authz0GroupNested
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        group: !Ref OwnerGroup
        nested: !Ref NestedGroup
```

In the `Value` you specify the ids of the group and the nested group.

## How do I add a member to a group?
You specify a CloudFormation resource of type `Custom::Authz0GroupMember`.

```yaml
  CustomerGroupMember:
    Type: Custom::Authz0GroupMember
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        group: !Ref CustomerGroup
        member: !Ref CustomerUser
```

In the `Value` you specify the ids of the group and the [member](user.md).

## How do I add a group mapping?
You specify a CloudFormation resource of type `Custom::Authz0GroupMapping`.

```yaml
  CustomerGroupMapping:
    Type: Custom::Authz0GroupMapping
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        group: !Ref MappedGroup
        groupName: other
        connectionName: google-oauth2
```

In the `Value` you specify the groupName and connection name of the mapping.


## How do I assign a role to a group?
You specify a CloudFormation resource of type `Custom::Authz0GroupRole`.

```yaml
  CustomerGroupRole:
    Type: Custom::Authz0GroupRole
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        group: !Ref CustomerGroup
        role: !Ref CustomerRole
```

In the `Value` you specify the ids of the group and the [role](role.md)
