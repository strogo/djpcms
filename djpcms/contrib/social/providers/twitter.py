import json

from djpcms import http
from djpcms.contrib import messages
from djpcms.utils.ajax import jerror, jhtmls
from djpcms.contrib.social import OAuthProvider


import tweepy


class Twitter(OAuthProvider):
    ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
    TWITTER_CHECK_AUTH = 'https://twitter.com/account/verify_credentials.json'

    def done(self, djp, key, secret):
        data    = djp.request.GET
        verifier = data.get('oauth_verifier', None)
        auth = self.twitter_auth()
        auth.set_request_token(key,secret)
        try:
            return auth.get_access_token(verifier)
        except:
            return None
        
    def user_data(self, request, access_token):
        request = self.oauth_request(request, access_token, self.TWITTER_CHECK_AUTH)
        data = self.fetch_response(request)
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
        
        
    def get_user_details(self, response):
        name = response['name']
        return {'uid': response['id'],
                'email': '',
                'username': response['screen_name'],
                'fullname': name,
                'first_name': name,
                'description': response.get('description',''),
                'location': response.get('location',''),
                'profile_image_url': response.get('profile_image_url',None),
                'url': response.get('url',None),
                'last_name': ''}

    def authenticated_api(self, key, secret):
        auth = tweepy.OAuthHandler(*self.tokens)
        auth.set_access_token(key, secret)
        return tweepy.API(auth)
