import os
import time
import logging
import auth0_provider
import authz_provider


logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))


def handler(request, context):
    time.sleep(0.1)     # Auth0 has a rate-limitation on the API
    if request['ResourceType'].startswith('Custom::Authz0'):
        return authz_provider.handler(request, context)
    else:
        return auth0_provider.handler(request, context)
