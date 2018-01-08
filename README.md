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
export AUTH0_DOMAIN=<....auth0.com without https>
export AUTH0_API_TOKEN=
export AWS_DEFAULT_PROFILE=<the profile you want>
export AWS_REGION=<the region you want>
```

Now create the application, by typing:
```
	./create-custom-auth0-provider-application
```
