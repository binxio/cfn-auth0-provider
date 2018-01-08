import requests
import logging
from datetime import datetime, timedelta

cache = {}


def get_access_token(tenant, client_id, client_secret):
    """
    retrieves an Auth0 access token for the specified tenant. The returned token is
    cached for the duration of the expires_in period, avoiding repetitive calls.
    """
    url = tenant[:-1] if tenant.endswith('/') else tenant
    key = '%s+%s+%s' % (url, client_id, client_secret)

    if key not in cache or cache[key][0] < datetime.now():
        body = {'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'audience': '%s/api/v2/' % url}

        r = requests.post('%s/oauth/token' % url, json=body)
        if r.status_code == 200:
            response = r.json()
            expires_at = datetime.now() + timedelta(seconds=response['expires_in'])
            cache[key] = (expires_at, response['access_token'])
        else:
            raise ValueError('error retrieving access token from %s, status code %d, %s' % (url, r.status_code, r.text))

    return cache[key][1]
