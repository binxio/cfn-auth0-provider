import os
import logging
import client_provider
import auth0_provider

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))


def handler(request, context):
    if request['ResourceType'] == 'Custom::Auth0Client':
        return client_provider.handler(request, context)
    else:
        return auth0_provider.handler(request, context)
