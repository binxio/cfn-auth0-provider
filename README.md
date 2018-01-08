# cfn-auth0-provider
A CloudFormation custom resource provider for managing Auth0.com resources.

When you deploy applications in Amazon ECS which uses Auth0.com for authentication and authorization, you need to configure Auth0 Clients and Resource Servers (APIs).
With this Custom CloudFormation Provider you can deploy applications and ECS Services from a single Cloudformation module.

## How do I deploy an Auth0 Client?
It is quite easy: you specify a CloudFormation resource of type [Custom::Auth0Client](docs/Auth0.md):

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
After the deployment, the client `cfn-auth0-petstore-client` can be found in your Auth0 tenant. The client id
can be obtained through `!GetAtt 'Client.ClientId'`.

## How do I deploy an Auth0 API?
You specify a CloudFormation resource of type [Custom::Auth0ResourceServer](docs/Auth0.md):

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
After the deployment, the api `cfn-auth0-petstore-api` is deployed in your Auth0 tenant.


## Installation
To install the custom resource provider, you first need to create an non-interactive application in Auth0
which is allowed to invoke the Auth0 Management API.

### Add Auth0 CloudFormation Provider application
Please get an [Auth0 administration API token](https://auth0.com/docs/api/management/v2/tokens#get-a-token-manually) manually, and set:

```
export AUTH0_DOMAIN=<....auth0.com without https>
export AUTH0_API_TOKEN=
export AWS_DEFAULT_PROFILE=<the profile you want>
export AWS_REGION=<the region you want>
```

Now create the application, by typing:
```
./create-custom-auth0-provider-application
```

This script will create the application in Auth0 and store its credentials of this application in the
[Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html) under
`/cfn-auth0-provider/tenant`, `/cfn-auth0-provider/client_id` and `/cfn-auth0-provider/client_secret`
respectively.


### Deploy the provider
To deploy the provider, type:

```sh
aws cloudformation create-stack \
        --capabilities CAPABILITY_IAM \
        --stack-name cfn-auth0-provider \
        --template-body file://cloudformation/cfn-auth0-provider.json

aws cloudformation wait stack-create-complete  --stack-name cfn-auth0-provider
```

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public/lambdas/cfn-auth0-provider-latest.zip`.

