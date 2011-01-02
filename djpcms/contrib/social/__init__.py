import cgi
import httplib2
import oauth2 as oauth
#from oauth import oauth

import djpcms
from djpcms import http
from djpcms.contrib import messages

provider_handles = {}


class SocialAuthenticationException(Exception):
    pass


def get(provider):
    return provider_handles.get(str(provider),None)


class SocialClient(object):
    
    def __init__(self, handler, instance):
        self.handler = handler
        self.instance = instance
        
    def __get_user(self):
        return self.instance.user
    user = property(__get_user)
    
    def delete(self):
        self.instance.delete()
        


class SocialProviderType(type):
    
    def __new__(cls, name, bases, attrs):
        abstract = attrs.pop('abstract',False)
        new_class = super(SocialProviderType, cls).__new__(cls, name, bases, attrs)
        if not abstract:
            for b in bases:
                if isinstance(b,SocialProviderType):
                    new_class()
                    break
        return new_class



class Provider(object):
    '''Social provider base class'''
    __metaclass__ = SocialProviderType
    client_class  = httplib2.Http
    
    def __init__(self):
        self.name = self.__class__.__name__.lower()
        from djpcms.conf import settings
        self.settings = settings
        consumers = getattr(settings,'SOCIAL_OAUTH_CONSUMERS',None)
        if consumers:
            consumers = consumers.get(self.name,None)
        if consumers:
            self.tokens = consumers
            provider_handles[self.name] = self
            
    def __str__(self):
        return self.name
    
    def cookie(self):
        return '%s-social' % self.name
        
    def request_url(self, djp):
        '''The request url'''
        raise NotImplementedError
        
    def get_user_details(self, response):
        raise NotImplementedError
    

class OAuthProvider(Provider):
    abstract = True
    auth_popup        = False
    
    REQUEST_METHOD    = 'GET'
    ACCESS_METHOD     = 'GET'
    REQUEST_TOKEN_URL = ''
    AUTHORIZATION_URL = ''
    ACCESS_TOKEN_URL  = ''
    SIGNATURE_METHOD  = oauth.SignatureMethod_HMAC_SHA1()
    DEFAULT_CONTENT_TYPE = 'application/x-www-form-urlencoded'
    
    OAuthToken = oauth.Token
    OAuthConsumer = oauth.Consumer
    OAuthRequest = oauth.Request
    
    def request_url(self, **kwargs):
        return self.REQUEST_TOKEN_URL
    
    def authorisation_url(self, **kwargs):
        return self.AUTHORIZATION_URL
    
    def access_url(self, **kwargs):
        return self.ACCESS_TOKEN_URL
        
    def extra_request_parameters(self):
        '''A dictionary of extra parameters to include in the OAUTH request.'''
        return {}
    
    def get_callback_url(self, token):
        if token:
            return token.get_callback_url()
        
    def fetch_request_token(self, callback, **kwargs):
        """Return request for unauthorized token.
        This is the first stage of the authorisation process"""
        oauth_request = self.oauth_request(None,
                                           self.request_url(**kwargs),
                                           callback = callback)
        response = self.fetch_response(oauth_request, self.REQUEST_METHOD)
        if response:
            token = self.OAuthToken.from_string(response)
            params = cgi.parse_qs(response, keep_blank_values=False)
            url = params.get('xoauth_request_auth_url',None)
            if url:
                token.set_callback(url[0])
            return token
        
    def fetch_authentication_uri(self, rtoken, **kwargs):
        """Second stage. Using the request token obtained from
:meth:`OAuthProvider.fetch_request_token` calculate the authorization `uri`."""
        uri = self.get_callback_url(rtoken)
        if not uri:
            uri = self.authorisation_url(**kwargs)
            if uri:
                request = self.oauth_request(rtoken, uri)
                uri = request.to_url()
        return uri
        
    def quick_access_token(self, data):
        return None
    
    def access_token(self, token, **kwargs):
        """Return request for access token value"""
        oauth_request = self.oauth_request(token, self.access_url(**kwargs))
        return self.OAuthToken.from_string(self.fetch_response(oauth_request,
                                                               self.ACCESS_METHOD))
    
    def user_data(self, request, access_token):
        """Loads user data from service"""
        raise NotImplementedError, 'Implement in subclass'
        
    def fetch_response(self, oauth_request, method = 'GET'):
        """Executes request and fetches service response"""
        connection = self.client_class()
        body = None
        headers = {}
        if method == "POST":
            headers['Content-Type'] = self.DEFAULT_CONTENT_TYPE
            body = oauth_request.to_postdata()
        elif method == "GET":
            uri = oauth_request.to_url()
        else:
            headers.update(oauth_request.to_header())

        request, response = connection.request(uri, method=method, body=body, 
                                               headers=headers)
        if request.status == 200:
            return response
        else:
            raise SocialAuthenticationException(response)
     
    def oauth_request(self, token, uri, callback = None):
        """Generate OAuth request, setups callback url"""
        consumer = self.consumer()
        parameters  = self.extra_request_parameters()
        if callback:
            parameters['oauth_callback'] = callback

        req = self.OAuthRequest.from_consumer_and_token(consumer,
                                                        token=token,
                                                        http_url=uri, 
                                                        parameters=parameters)
        req.sign_request(self.SIGNATURE_METHOD, consumer, token)
        return req
    
    def consumer(self):
        return self.OAuthConsumer(*self.tokens)
    
    def authtoken(self, key, secret, verifier = None):
        '''Create the authentication token to use for obtaining the Access Token.'''
        token = self.OAuthToken(key,secret)
        if verifier:
            token.set_verifier(verifier)
        return token
    
    def get_access_token_key(self, access_token):
        return access_token.key
    
    def authenticated_api(self, key, secret):
        raise NotImplementedError
    

    
    