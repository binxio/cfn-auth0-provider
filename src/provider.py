import os
import logging
import auth0_provider

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))


def handler(request, context):
    return auth0_provider.handler(request, context)
