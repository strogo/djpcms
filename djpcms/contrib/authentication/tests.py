from django import forms, http
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from djpcms.models import SiteContent
from djpcms.views import appsite
from providers import providers, OAuthProvider, LoginBase, oauth
from appurl import OAuthApplication


class OAuthSandbox(OAuthProvider):
    description       = 'OAuth Sandbox for testing'
    consumer_key      = '57145cab582a2469'
    consumer_secret   = '713ac825ce2816713e4f9c07beb7'
    request_token_url = 'http://oauth-sandbox.sevengoslings.net/request_token'
    authorize_url     = 'http://oauth-sandbox.sevengoslings.net/authorize' 
    access_token_url  = 'http://oauth-sandbox.sevengoslings.net/access_token'
    
    class Login(LoginBase):
        username = forms.CharField()
        password = forms.CharField(widget=forms.PasswordInput)


providers.append(OAuthSandbox())


class TestClientLogin(TestCase):
    
    def setUp(self):
        pass
        
    def provider(self, provider):
        return providers.get(provider)
    
    def process(self, provider):
        baseurl = '/accounts/login/%s/' % provider
        p = self.provider(provider)
        data = p.initial()
        data.update({'username': 'john', 'password': 'smith'})
        res = self.client.post(baseurl, data)
        url = res._headers['location'][1]
        client = oauth.Client(p.consumer())
        response, content = client.request(url)
        self.assertEqual(response.status,200)        
        
    def testOauthSandbox(self):
        self.process('oauthsandbox')
        
    def testTwitter(self):
        self.process('twitter')
        