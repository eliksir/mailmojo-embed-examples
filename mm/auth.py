from oauthlib.oauth2 import (WebApplicationClient, LegacyApplicationClient,
                             BackendApplicationClient)
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth


class Auth:
    AUTHORIZE_ENDPOINT = 'https://api.mailmojo.no/oauth/authorize/'
    TOKEN_ENDPOINT = 'https://api.mailmojo.no/oauth/token/'

    @classmethod
    def get_authorization_url(cls, client_id, redirect_uri, scope):
        """Return URL for Authorization Code Flow."""

        oauth = OAuth2Session(
            client=WebApplicationClient(client_id),
            redirect_uri=redirect_uri,
            scope=scope
        )
        url, _ = oauth.authorization_url(cls.AUTHORIZE_ENDPOINT)
        return url

    @classmethod
    def get_backend_token(cls, client_id, client_secret, scope):
        """Return token for a Client Credentials Grant."""

        oauth = OAuth2Session(client=BackendApplicationClient(client_id))
        return oauth.fetch_token(
            cls.TOKEN_ENDPOINT,
            auth=HTTPBasicAuth(client_id, client_secret),
            scope=scope
        )

    @classmethod
    def get_legacy_token(cls, client_id, client_secret, **kwargs):
        """Return a token for legacy application client."""

        oauth = OAuth2Session(client=LegacyApplicationClient(client_id))
        return oauth.fetch_token(
            cls.TOKEN_ENDPOINT,
            auth=HTTPBasicAuth(client_id, client_secret),
            **kwargs
        )

    @classmethod
    def get_legacy_refresh_token(cls, client_id, client_secret, **kwargs):
        """Return refresh token for legacy application client."""

        oauth = OAuth2Session(client=LegacyApplicationClient(client_id))
        return oauth.refresh_token(
            cls.TOKEN_ENDPOINT,
            auth=HTTPBasicAuth(client_id, client_secret),
            **kwargs
        )

    @classmethod
    def get_web_token(cls, client_id, client_secret, code, redirect_uri,
                      state):
        """Return a token for an Authorization Code Grant."""

        oauth = OAuth2Session(
            client=WebApplicationClient(client_id),
            redirect_uri=redirect_uri,
            state=state,
        )
        return oauth.fetch_token(
            cls.TOKEN_ENDPOINT,
            code=code,
            auth=HTTPBasicAuth(client_id, client_secret)
        )
