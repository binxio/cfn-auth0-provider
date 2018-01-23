## How do I deploy a Client grant?
You specify a CloudFormation resource of type `Custom::Auth0ClientGrant`.

```yaml
  ClientGrant:
    Type: Custom::Auth0ClientGrant
    DependsOn: [ Client, API ]
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value: 
        client_id: !Ref Client
        audience: 'https://github.com/binxio/cfn-auth0-provider/petstore'
        scope:
          - get:pets
```
In the `Value` you can specify all of the properties for the [Create a client grant](https://auth0.com/docs/api/management/v2#!/Client_Grants/post_client_grants) operation.

