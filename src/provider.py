import os
import time
import logging
import auth0_provider
import authz_provider
import auth0_email_provider


logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))


def handler(request, context):
    time.sleep(0.1)     # Auth0 has a rate-limitation on the API
    request_type = request['ResourceType']
    if request_type.startswith('Custom::Authz0'):
        return authz_provider.handler(request, context)
    elif request_type == 'Custom::Auth0EmailProvider':
        return auth0_email_provider.handler(request, context)
    else:
        return auth0_provider.handler(request, context)
