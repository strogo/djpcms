import json
from flickrapi import FlickrAPI

from djpcms.contrib.social import OAuthProvider


DEFAULT_FLICKR_PERMISSION = 'read'


class Flickr(OAuthProvider):
    AUTHORIZATION_URL = 'http://www.flickr.com/services/auth/'
    
    def extra_request_parameters(self):
        perms = getattr(self.settings,'FLICKR_PERMISSION',DEFAULT_FLICKR_PERMISSION)
        return {'perms':perms}
    
    def fetch_request_token(self, callback, **kwargs):
        return None
    
    def fetch_authentication_uri(self, rtoken, **kwargs):
        api = FlickrAPI(*self.tokens)
        params = self.extra_request_parameters()
        params['api_key'] = self.tokens[0]
        data = api.encode_and_sign(params)
        return '{0}?{1}'.format(self.authorisation_url(**kwargs),data)
    
    def quick_access_token(self, data):
        api = self._get_api()
        frob = data.get('frob',None)
        res = api.auth_getToken(frob=frob)
        res = json.loads(res[14:-1])
        return res['auth']
    
    def get_access_token_key(self, access_token):
        return access_token['token']['_content']
    
    def user_data(self, access_token):
        token = self.get_access_token_key(access_token)
        uuid  = access_token['user']['nsid']
        api = self.authenticated_api(token)
        res = json.loads(api.people_getInfo(user_id = uuid)[14:-1])
        return res,token,''
        
    def authenticated_api(self, key, secret = None):
        return self._get_api(token = key)
    
    def _get_api(self, token = None):
        kwargs = {'format':'json','token':token}
        return FlickrAPI(*self.tokens, **kwargs)
    
    def get_user_details(self, response):
        response = response['person']
        name = response['realname']['_content']
        return {'uid': response['nsid'],
                'email': '',
                'username': response['username']['_content'],
                'fullname': name,
                'first_name': name,
                'description': '',
                'location': response['location']['_content'],
                'url': response['profileurl']['_content']}
