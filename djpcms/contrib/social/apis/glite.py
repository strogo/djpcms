'''
A light google data API
'''
import oauth


class Auth(object):
    
    def __init__(self, consumer):
        self.consumer = consumer
        self.access_token = None

    def set_access_token(self, key, secret):
        self.access_token = oauth.OAuthToken(key, secret)
        
        
class Api(object):
    
    def __init__(self, auth):
        self.auth = auth
          
    