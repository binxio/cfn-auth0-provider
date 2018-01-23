## How do I deploy an Auth0 Rule?
You specify a CloudFormation resource of type `Custom::Auth0Rule`.

```yaml
  Rule:
    Type: Custom::Auth0Rule
    Properties:
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-auth0-provider'
      Value:
        name: 'cfn-auth0-petstore-rule'
        enabled: false
        script: |
          function (user, context, callback) {
            // do want you need to do here
            callback(null, user, context);
          }
```
In the `Value` you can specify all of the properties for the [Create a rule](https://auth0.com/docs/api/management/v2#!/Rules/post_rules) operation.

