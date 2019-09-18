from facebook_credintials import CLIENT_ID, CLIENT_SECRET, APP_TOKEN
_AUTHORIZATION_BASE_URI = 'https://www.facebook.com/v4.0/dialog/oauth?'
_TOKEN_URL = 'https://graph.facebook.com/v4.0/oauth/access_token?'
_REDIRECT_URI = 'http://localhost:8000/auth/facebook/callback'
_SCOPE = ['public_profile', 'email']

# called with delete method
_REVOKE_URL = 'https://graph.facebook.com/me/permissions'

# use this to validate access token - belong to your app and generated by your user
_INSPECT_TOKEN_URL = 'https://graph.facebook.com/debug_token?'

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

    def inspect_token(self, input_token, app_token=APP_TOKEN):
        '''
        inspect token info : param : 
        input_token: token to inspect
        access_token: app-access token
        return data about the ispected token
        '''
        r = self.get(_INSPECT_TOKEN_URL, input_token=input_token, access_token=app_token).json()
        pass
    
    def profile(self):
        '''
        return a dict object:
        keys: facebook_id, name, email,piture all string
        '''
        profile = self.get(_PROFILE_URL).json()
        profile['facebook_id'] = int(profile['id'])
        profile['picture'] = profile.get('picture').get('data').get('url')
        # TODO : add 'access_token' key to profile dict 
        # profile['access_token'] = self.token
        return profile

    def revoke(self):
        return self.delete(_REVOKE_URL) 

    @classmethod
    def authorized_session(cls, token):
        session = cls(token=token)
        return session