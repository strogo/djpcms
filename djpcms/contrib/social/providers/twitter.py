import json

from django import http
from djpcms.contrib import messages

from djpcms import forms
from djpcms.utils.uniforms import FormLayout, Fieldset, nolabel
from djpcms.views import appview
from djpcms.utils.ajax import jerror, jhtmls
from djpcms.contrib.social import OAuthProvider

#import tweepy


class MessageForm(forms.Form):
    message = forms.CharField(widget = forms.Textarea(attrs = {'class':'twitter-box-editor'}))
    submits = (('tweet','tweet'),)
    layout = FormLayout(Fieldset('message',css_class=nolabel))

def post_tweet(user,msg):
    pass



class Twitter(OAuthProvider):
    ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
    TWITTER_CHECK_AUTH = 'https://twitter.com/account/verify_credentials.json'

    def twitter_auth(self):
        return tweepy.OAuthHandler(*self.tokens)
    
    def __authorisation_url(self, **kwargs):
        auth          = self.twitter_auth()
        signin_url    = auth.get_authorization_url()
        request_token = auth.request_token
        token_tup     = (request_token.key,request_token.secret)
        return token_tup,signin_url

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




class TwitterPostView(appview.ModelView):
    _form = MessageForm
    _form_ajax = True
    
    def render(self, djp, **kwargs):
        return self.get_form(djp,**kwargs).render(djp)
    
    def get_auth(self, user):
        if user.is_authenticated() and user.is_active:
            twitter = user.linked_accounts.filter(provider = 'twitter')
            if twitter:
                twitter = twitter[0]
            else:
                return None
            return twitter_auth(**twitter.data)
        
    def default_post(self, djp):
        auth = self.get_auth(djp.request.user)
        if not auth:
            return jerror('Could not authenticate twitter')
        api = tweepy.API(auth)
        f = self.get_form(djp)
        if not f.is_valid():
            return jerror('Could not authenticate twitter')
        msg  = f.cleaned_data['message']
        api.update_status(msg)
        return jhtmls(identifier = '.twitter-box-editor', html = '', type = 'value')

