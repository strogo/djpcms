import oauth
import urlparse

from djpcms.contrib.social import OAuthProvider
from djpcms.contrib.social.apis import YahooApi


class Yahoo(OAuthProvider):
    REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
    AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth/v2/request_auth'
    ACCESS_TOKEN_URL  = 'https://api.login.yahoo.com/oauth/v2/get_token'
    
    def user_data(self, access_token):
        api = YahooApi(self, access_token)
        guid = api.user_id()
        data = api.user_data(guid)
        return data,access_token.key,access_token.secret
    
    def authenticated_api(self, key, secret):
        token = self.OAuthToken(key, secret)
        return YahooApi(self, token)
    
    def get_user_details(self, response):
        return {'uid': response['guid']}