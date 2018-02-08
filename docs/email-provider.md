## How do I configure the Auth0 Email provider?
To configure the email provider, you specify a CloudFormation resource of type `Custom::Auth0EmailProvider`, using the following syntax:

```yaml
  Client:
    Type: Custom::Auth0EmailProvider
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        name: mandrill,
        enabled: true,
        default_from_address: no-reply@me.com
        credentials: {}
        settings: {}

```
In the `Value` you can specify all of the properties for the [Configure an email provider](https://auth0.com/docs/api/management/v2#!/Emails/post_provider).

Please note that the email provider is singleton value.
