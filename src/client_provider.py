import logging
from auth0_provider import Auth0Provider
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


log = logging.getLogger(name=__name__)


class Auth0ClientProvider(Auth0Provider):

    def __init__(self):
        super(Auth0ClientProvider, self).__init__()

    def set_attributes_from_returned_value(self, client):
        """
        set the ClientId and the PublicKeyPEM attributes, so that they can be
        used by other resources
        """
        self.set_attribute('Tenant', self.tenant)
        self.set_attribute('ClientId', client['client_id'])
        keys = client['signing_keys'] if 'signing_keys' in client else []
        if len(keys) > 0 and 'cert' in keys[0]:
            cert = x509.load_pem_x509_certificate(str(keys[0]['cert']), default_backend())
            pem = cert.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo)
            self.set_attribute('PublicKeyPEM', pem)

provider = Auth0ClientProvider()


def handler(request, context):
    return provider.handle(request, context)
