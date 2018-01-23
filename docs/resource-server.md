## How do I deploy an Auth0 API?
You specify a CloudFormation resource of type `Custom::Auth0ResourceServer`.

```yaml
  API:
    Type: Custom::Auth0ResourceServer
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value: 
        name: cfn-auth0-petstore-api
        identifier: https://github.com/binxio/cfn-auth0-provider/petstore
        allow_offline_access: false
        skip_consent_for_verifiable_first_party_clients: true
        token_lifetime: 900
        token_lifetime_for_web: 900
        signing_alg: RS256
        scopes:
          - {value: 'create:pets', description: 'add pets'}
          - {value: 'update:pets', description: 'update pets'}
          - {value: 'get:pets', description: 'get pets'}
          - {value: 'delete:pets', description: 'delete pets'}
          - {value: 'list:pets', description: 'list all pets'}
```

In the `Value` you can specify all of the properties for the [Create a resource server](https://auth0.com/docs/api/management/v2#!/Resource_Servers/post_resource_servers) operation.  

