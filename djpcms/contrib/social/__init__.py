import httplib2
from oauth import oauth

from django import http
from django.contrib import messages

import djpcms
from .defaults import User

provider_handles = {}


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
    connection    = httplib2.Http()
    
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
    
    def done(self, djp, oauth_token, key, secret):
        data    = djp.request.GET
        verifier = data.get('oauth_verifier', None)
    
        # If the token from session and token from twitter does not match
        # means something bad happened to tokens
        if key != oauth_token:
            messages.info(request, "Token for session and from twitter don't mach. Could not login.")
            # Redirect the user to the login page
            return http.HttpResponseRedirect('/')
    
        auth = twitter_auth()
        auth.set_request_token(key,secret)
        try:
            access_token = auth.get_access_token(verifier)
        except:
            return
        user = request.user
        acc  = user.linked_accounts.filter(provider = 'twitter')
        if acc:
            acc = acc[0]
        else:
            acc = LinkedAccount(user = user, provider = 'twitter')
        acc.data = {'key':access_token.key,'secret':access_token.secret}
        acc.save()
    
        # authentication was successful, use is now logged in
        next = request.session.get('twitter_login_next', None)
        if next:
            del_dict_key(request.session, 'twitter_login_next')
            return http.HttpResponseRedirect(next)
        else:
            home = '%s%s' % (settings.USER_ACCOUNT_HOME_URL,user.username)
            return http.HttpResponseRedirect(home)
        
    def get_user_details(self, response):
        raise NotImplementedError
        
    def client(self, **kwargs):
        raise NotImplentedError
    
    

class OAuthProvider(Provider):
    abstract = True
    REQUEST_TOKEN_URL = ''
    AUTHORIZATION_URL = ''
    ACCESS_TOKEN_URL  = ''
    
    def redirect_uri(self, request):
        uri = djpcms.get_url(User, 'social_done', provider = self.name)
        return '%s://%s%s' % ('https' if request.is_secure() else 'http', request.get_host(), uri)
    
    def request_url(self, **kwargs):
        return self.REQUEST_TOKEN_URL
    
    def authorisation_url(self, **kwargs):
        return self.AUTHORIZATION_URL
    
    def access_url(self, **kwargs):
        return self.ACCESS_TOKEN_URL
        
    def unauthorized_token(self, request, **kwargs):
        """Return request for unauthorized token. This is the first stage of the authorisation process"""
        oauth_request = self.oauth_request(request, None, self.request_url(**kwargs))
        response = self.fetch_response(oauth_request)
        if response:
            r = oauth.OAuthToken.from_string(response)
            setattr(r,'callback',oauth_request.parameters['oauth_callback'])
            return r
        
    def authenticate(self, request, utoken, **kwargs):
        """Second stage. Using the unauthorised token redirect to authentication page."""
        signin_url = self.authorisation_url(**kwargs)
        oauth_callback = utoken.callback
        request.session['request_token'] = (utoken.key,utoken.secret)
        if signin_url:
            signin_url = self.oauth_request(request, utoken, signin_url, **kwargs).to_url()
            return http.HttpResponseRedirect(str(signin_url))
        else:
            return http.HttpResponseRedirect(oauth_callback)
        
    def access_token(self, request, token, **kwargs):
        """Return request for access token value"""
        oauth_request = self.oauth_request(request, token, self.access_url(**kwargs))
        return oauth.OAuthToken.from_string(self.fetch_response(oauth_request))
    
    def user_data(self, request, access_token):
        """Loads user data from service"""
        raise NotImplementedError, 'Implement in subclass'
    
    def get_user_id(self, details, response):
        return details.get('uid','')
    
    def fetch_response(self, request):
        """Executes request and fetchs service response"""
        request, response = self.connection.request(request.to_url(), method = request.http_method)
        if request.status == 200:
            return response
     
    def oauth_request(self, request, token, url, extra_params=None):
        """Generate OAuth request, setups callback url"""
        if not token:
            oauth_callback = self.redirect_uri(request)
            params = {'oauth_callback': oauth_callback}
        else:
            params = {}
        if extra_params:
            params.update(extra_params)

        if 'oauth_verifier' in request.GET:
            params['oauth_verifier'] = request.GET['oauth_verifier']
        consumer = self.consumer()
        request = oauth.OAuthRequest.from_consumer_and_token(consumer,
                                                             token=token,
                                                             http_url=url,
                                                             parameters=params)
        request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),consumer,token)
        return request
    
    def consumer(self):
        return oauth.OAuthConsumer(*self.tokens)
    
    def authtoken(self, ttoken):
        '''Auth token from a tuple key,secret'''
        token = oauth.OAuthConsumer(*ttoken)
        setattr(token,'callback',None)
        setattr(token,'verifier',None)
        return token
    
    
        
def client(user, provider):
    if not isinstance(user,User):
        user = User.objects.get(username = user)
    p = user.linked_accounts.get(provider = str(provider))
    handler = provider_handles[p.provider]
    return SocialClient(handler,p)
    
    