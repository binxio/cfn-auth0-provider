# cfn-auth0-provider
A custom resource provider for Auth0 resources.


## Installation
To install these custom resources, type:

```sh
aws cloudformation create-stack \
        --capabilities CAPABILITY_IAM \
        --stack-name cfn-auth0-provider \
        --template-body file://cloudformation/cfn-auth0-provider.json

aws cloudformation wait stack-create-complete  --stack-name cfn-auth0-provider
```

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public/lambdas/cfn-auth0-provider-latest.zip`.

## Preparing Auth0
Before you can use the resource provider, you need to create an Auth0 application which is privileged to manage resources in Auth0 in 
your account.


### Obtaining Admin API token
Please get an [Auth0 administration API token](https://auth0.com/docs/api/management/v2/tokens#get-a-token-manually) manually, and set:

```
export AUTH0_DOMAIN=....auth0.com
export AUTH0_API_TOKEN=
```

### Creating the non interactive application
Now you can create the non-interactive application to represent your CloudFormation Auth0 resource provider:

```
curl --header "authorization: bearer $AUTH0_API_TOKEN" \
     --header 'content-type: application/json' \
     -X POST \
     -d @- \
     https://$AUTH0_DOMAIN/api/v2/clients <<!
{
  "name": "Auth0 CloudFormation Provider",
  "app_type": "non_interactive"
}
!
```

Obtain the client id of your newly created application:

```
CLIENT_ID=$(curl -sS -H "authorization: Bearer $AUTH0_API_TOKEN" \
				https://$AUTH0_DOMAIN/api/v2/clients | \
		jq -r '.[] | select(.name == "Auth0 CloudFormation Provider") | .client_id')

CLIENT_SECRET=$(curl -sS -H "authorization: Bearer $AUTH0_API_TOKEN" \
				https://$AUTH0_DOMAIN/api/v2/clients | \
		jq -r '.[] | select(.name == "Auth0 CloudFormation Provider") | .client_secret')
```

Grant the appropriate permissions to the application:
```
curl --header "authorization: Bearer $AUTH0_API_TOKEN" \
     --header 'content-type: application/json' \
     -X POST \
     -d @- \
     https://$AUTH0_DOMAIN/api/v2/client-grants <<!
{
    "client_id": "$CLIENT_ID",
    "audience": "https://$AUTH0_DOMAIN/api/v2/",
    "scope": [
      "read:client_grants",
      "create:client_grants",
      "delete:client_grants",
      "update:client_grants",
      "read:clients",
      "update:clients",
      "delete:clients",
      "create:clients",
      "read:connections",
      "update:connections",
      "delete:connections",
      "create:connections",
      "read:resource_servers",
      "update:resource_servers",
      "delete:resource_servers",
      "create:resource_servers",
      "read:rules",
      "update:rules",
      "delete:rules",
      "create:rules"
    ]
  }
!

Store the resulting tenant, client id and secret in the Parameter store:

```
   aws ssm put-parameter --name /cfn-auth0-provider/tenant --type SecureString --value=$AUTH0_DOMAIN
   aws ssm put-parameter --name /cfn-auth0-provider/client_id --type SecureString --value=$CLIENT_ID
   aws ssm put-parameter --name /cfn-auth0-provider/client_secret --type SecureString --value=$CLIENT_SECRET
```
