from urlparse import urlparse
import httplib2

import flick
from django import http
from djpcms.contrib import messages

from djpcms import forms
from djpcms.utils.uniforms import FormLayout, Fieldset, nolabel
from djpcms.views import appview
from djpcms.utils.ajax import jerror, jhtmls

from djpcms.contrib.social import SocialProvider


class Flickr(SocialProvider):
    
    def request_url(self, djp, callback_url = None, **kwargs):
        r = djp.request
        p = OAuthInputParams('HMAC_SHA1',*self.tokens)
        url = GenerateOAuthRequestTokenUrl(p,self.scopes)
        r = httplib2.Http()
        response, content = r.request(str(url))
        if response.status == 200:
            token = OAuthTokenFromHttpBody(content)
            url = GenerateOAuthAuthorizationUrl(token, callback_url = callback_url)
            return (token.key,token.secret),url
        else:
            return None,None
        
    def done(self, djp, key, secret):
        p = OAuthInputParams('HMAC_SHA1',*self.tokens)
        token = OAuthToken(key, secret, self.scopes)
        url = GenerateOAuthAccessTokenUrl(token,p)
        r = httplib2.Http()
        response, content = r.request(str(url))
        if response.status == 200:
            return OAuthTokenFromHttpBody(content)
        else:
            return None
        
        
    def client(self, key = None, secret = None, **kwargs):
        tks = {}
        ot  = OAuthToken(key, secret, self.scopes)
        for scope in self.scopes:
            tks[scope] = ot
        store = TokenStore(tks)
        pass
    

Google()