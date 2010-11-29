from djpcms.test import TestCase
from djpcms.conf import settings
from djpcms.contrib.social.defaults import User
from djpcms.contrib.social import OAuthProvider
from djpcms.contrib.social.applications import SocialUserApplication


appurls = SocialUserApplication('/accounts/', User),


class oauthtest(OAuthProvider):
    '''Test server from http://term.ie/oauth/example/'''
    REQUEST_TOKEN_URL = 'http://term.ie/oauth/example/request_token.php'
    ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'


class SocialTest(TestCase):
    appurls = 'djpcms.contrib.social.tests'
    
    def testRequest(self):
        pass
        #self.get('/accounts/oauthtest/login/')
    