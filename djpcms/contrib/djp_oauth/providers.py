import urlparse
import urllib

from django import forms, http

from django_openid.registration import RegistrationConsumer 

import oauth2 as oauth

from djpcms.template import loader
from djpcms.utils.html import formlet
import settings


class ProviderBase(object):
    form = None
    
    def name(self):
        return self.__class__.__name__.lower()

    def __str__(self):
        return self.name()
    
    def id(self):
        return u'login-%s' % self.name()
    
    def render(self, request, path, rest_of_url):
        if self.form:
            f = self.form()
            return formlet(form = f)
        else:
            return ''

    def process(self, request, data):
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
        
    

class twitter(OAuthProvider):
    description       = 'Twitter'
    consumer_key      = settings.TWITTER_CONSUMER_KEY
    consumer_secret   = settings.TWITTER_CONSUMER_SECRET
    request_token_url = 'http://twitter.com/oauth/request_token'
    access_token_url  = 'http://twitter.com/oauth/access_token'
    authorize_url     = 'http://twitter.com/oauth/authorize'
        
    def fetch_request_token(self, callback):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, callback = callback, http_url=self.request_token_url)
        oauth_request.sign_request(self.signature_method, self.consumer, None)
        params = oauth_request.parameters
        data = urllib.urlencode(params)
        full_url='%s?%s'%(self.request_token_url, data)
        response = urllib2.urlopen(full_url)
        return oauth.OAuthToken.from_string(response.read())
        


class OpenIdConsumer(RegistrationConsumer):
    
    def __call__(self, request, rest_of_url):
        if not rest_of_url:
            return self.do_login(request)
        elif rest_of_url == 'logo':
            return self.do_logo(request)
        elif rest_of_url == 'complete':
            return self.do_complete(request)
        else:
            pass


class openid(ProviderBase):
    description = 'Open ID'
    
    def __init__(self):
        self.consumer = OpenIdConsumer()
    
    def process(self, request, data):
        url = data.get('openid_url',None)
        if not url:
            return
        request.session['openid_url'] = url
        return self.consumer.start_openid_process(request, url)
        
    def render(self, request, path, rest_of_url):
        if not rest_of_url:
            return loader.render_to_string('djp_oauth/openid.html', {'url': path})
        return self.consumer(request, rest_of_url)
        
        
        
        
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