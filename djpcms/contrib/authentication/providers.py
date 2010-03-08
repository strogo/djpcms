import urlparse
import urllib

from django import forms, http

import oauth2 as oauth

from djpcms.utils.html import formlet
import settings


class LoginBase(forms.Form):
    provider = forms.CharField(widget = forms.HiddenInput(), required = True)



class ProviderBase(object):
    
    def name(self):
        return self.__class__.__name__.lower()

    def __str__(self):
        return self.name()
    
    def id(self):
        return u'login-%s' % self.name()
    
    def initial(self):
        return {'provider': self.name()}
    
    def render(self):
        f = self.Login(initial = self.initial)
        return formlet(form = f)

    def process(self, request, **kwargs):
        raise NotImplementedError


class OAuthProvider(ProviderBase):
    consumer_key      = None
    consumer_secret   = None
    request_token_url = None
    access_token_url  = None
    authorize_url     = None
    
    def consumer(self):
        return oauth.Consumer(self.consumer_key, self.consumer_secret)
    
    def process(self, request, **kwargs):
        consumer = self.consumer()
        client = oauth.Client(consumer)
        resp, content = client.request(self.request_token_url, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        request_token = dict(urlparse.parse_qsl(content))
        oauth_token = request_token['oauth_token']
        request.session['oauth_token'] = oauth_token 
        #
        # Redirect to provider       
        url = "%s?oauth_token=%s" % (self.authorize_url, oauth_token)
        return http.HttpResponseRedirect(url)
        
    

class twitter(OAuthProvider):
    description       = 'Twitter'
    consumer_key      = settings.TWITTER_CONSUMER_KEY
    consumer_secret   = settings.TWITTER_CONSUMER_SECRET
    request_token_url = 'http://twitter.com/oauth/request_token'
    access_token_url  = 'http://twitter.com/oauth/access_token'
    authorize_url     = 'http://twitter.com/oauth/authorize'
    
    class Login(LoginBase):
        username = forms.CharField(label = 'twitter username')
        password = forms.CharField(widget=forms.PasswordInput, label = 'twitter password')
        
    def fetch_request_token(self, callback):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, callback = callback, http_url=self.request_token_url)
        oauth_request.sign_request(self.signature_method, self.consumer, None)
        params = oauth_request.parameters
        data = urllib.urlencode(params)
        full_url='%s?%s'%(self.request_token_url, data)
        response = urllib2.urlopen(full_url)
        return oauth.OAuthToken.from_string(response.read())
    
    def process(self, request, twitter_username = None, twitter_passsword = None, **kwargs):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        client = oauth.Client(consumer)
        resp, content = client.request(self.request_token_url, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        request_token = dict(urlparse.parse_qsl(content))
        oauth_token = request_token['oauth_token']
        request.session['oauth_token'] = oauth_token 
        #
        # Redirect to provider       
        url = "%s?oauth_token=%s" % (self.authorize_url, oauth_token)
        return http.HttpResponseRedirect(url)
        


        

class openid(ProviderBase):
    description = 'Open ID'
    
    class Login(LoginBase):
        open_id = forms.CharField(label = 'Open ID')
        
        
class Providers(object):
    
    def __init__(self):
        self.list = []
        self.dict = {}
    
    def get(self, name):
        return self.dict.get(name,None)
    
    def append(self, p):
        self.list.append(p)
        self.dict[p.name()] = p
        
    def choices(self):
        for p in self.list:
            yield (p.__class__.__name__,p.description)


providers = Providers()
providers.append(twitter())
providers.append(openid())