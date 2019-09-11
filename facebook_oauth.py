from facebook_credintials import CLIENT_ID, CLIENT_SECRET
_AUTHORIZATION_BASE_URI = 'https://www.facebook.com/v4.0/dialog/oauth?'
_TOKEN_URL = 'https://graph.facebook.com/v4.0/oauth/access_token?'
_REDIRECT_URI = 'http://localhost:8000/auth/facebook/callback'
_SCOPE = ['public_profile', 'email']

# called with delete method
_REVOKE_URL = 'https://graph.facebook.com/me/permissions'

# use this to validate access token - belong to your app and generated by your user
_DEBUG_TOKEN_URL = 'https://graph.facebook.com/debug_token?input_token={access-token}&access_token={app-token}'

_PROFILE_URL = 'https://graph.facebook.com/me?fields=name,email,picture'

from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import facebook_credintials

class FaceBookOauthSession(OAuth2Session):
    def __init__(self, client_id=CLIENT_ID, scope=_SCOPE, redirect_uri=_REDIRECT_URI, token=None, state=None):
            super().__init__(client_id=client_id, scope=scope, redirect_uri=redirect_uri, token=token, state=state)
            self = facebook_compliance_fix(self)

    def authorization_url(self):
        return OAuth2Session.authorization_url(self, _AUTHORIZATION_BASE_URI)

    def fetch_token(self, token_url=_TOKEN_URL, code=None, authorization_response=None, body='', auth=None, username=None, password=None, method='POST', timeout=None, headers=None, verify=True, proxies=None, include_client_id=None, client_secret=CLIENT_SECRET, **kwargs):
        return OAuth2Session.fetch_token(self, token_url, authorization_response=authorization_response, client_secret=client_secret)

    def profile(self):
        return self.get(_PROFILE_URL).json()

    def revoke(self):
        return self.delete(_REVOKE_URL) 

    @classmethod
    def authorized_session(cls, token):
        session = cls(token=token)
        return session