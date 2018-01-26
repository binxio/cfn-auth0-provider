# cfn-auth0-provider
A CloudFormation custom resource provider for managing Auth0.com resources.  When you deploy applications in Amazon ECS which uses Auth0.com for authentication and authorization, you need to configure Auth0 Clients and Resource Servers (APIs).  With this Custom CloudFormation Provider you can deploy applications, ECS Services and the Auth0 configuration from a single Cloudformation module.

The provider supports both the Auth0 resources from the: 

- Management API through [Custom::Auth0](docs/auth0.md).
- Authorization extension API through [Custom::Authz0](docs/authz0.md).

## Installation
To install the custom resource provider, you first need to create an non-interactive application in Auth0
which is allowed to invoke the Auth0 Management API.

### Add Auth0 CloudFormation Provider application
Please get an [Auth0 administration API token](https://auth0.com/docs/api/management/v2/tokens#get-a-token-manually) manually, and set the
following environment variables:

```
export AUTH0_API_TOKEN=
```

### Add the Authorization Extension in Auth0
Unfortunately, we cannot add the authorization extension programmatically. Please follow the [Auth0 Authorization Extension installation instructions](https://auth0.com/docs/extensions/authorization-extension/v2/implementation/installation) and set the environment variable `AUTH0_AUTHZ_API` to point to the API.

```
export AUTH0_AUTHZ_API=<url of the authorization extension API>
```

At the moment of writing, the URL for the installation Authorization Extension version 2.4 is:
```
export  AUTH0_AUTHZ_API=https://${AUTH0_DOMAIN/auth0.com/webtask.io}/adf6e2f2b84784b57522e3b19dfc9201
```

### 

Now create the application, by typing:
```
./bin/create-custom-auth0-provider-application -d $AUTH0_DOMAIN \
		-p $AWS_DEFAULT_PROFILE \
		-r $AWS_DEFAULT_REGION  \
		-u $AUTH0_AUTHZ_URL
```

This script will create the application in Auth0 and store its credentials of this application in the
[Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html) under
`/cfn-auth0-provider/tenant`, `/cfn-auth0-provider/client_id` and `/cfn-auth0-provider/client_secret`
respectively. The Authorization extension API URL will be stored under `/cfn-auth0-provider/authorization_url`


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

