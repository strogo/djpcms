import oauth
import urlparse

from djpcms.contrib.social import OAuthProvider
#from djpcms.contrib.social.libs import YahooApi


class Yahoo(OAuthProvider):
    REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
    AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth/v2/request_auth'
    ACCESS_TOKEN_URL  = 'https://api.login.yahoo.com/oauth/v2/get_token'
        
    def authenticated_api(self, key, secret):
        auth = tweepy.OAuthHandler(*self.tokens)
        auth.set_access_token(key, secret)
        return YahooApi(auth)
    