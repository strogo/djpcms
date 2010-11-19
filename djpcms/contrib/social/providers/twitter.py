from django import http
from djpcms.contrib import messages

from djpcms import forms
from djpcms.utils.uniforms import FormLayout, Fieldset, nolabel
from djpcms.views import appview
from djpcms.utils.ajax import jerror, jhtmls

from djpcms.conf import settings

TWITTER_CONSUMER_TOCKEN = getattr(settings,'TWITTER_CONSUMER_TOCKEN',None)
TWITTER_CONSUMER_SECRET = getattr(settings,'TWITTER_CONSUMER_SECRET',None)

from djpcms.contrib.social import SocialProvider


import tweepy

def del_dict_key(src_dict, key):
    if key in src_dict:
        del src_dict[key]


class MessageForm(forms.Form):
    message = forms.CharField(widget = forms.Textarea(attrs = {'class':'twitter-box-editor'}))
    submits = (('tweet','tweet'),)
    layout = FormLayout(Fieldset('message',css_class=nolabel))

def post_tweet(user,msg):
    pass



class Twitter(SocialProvider):

    def twitter_auth(self):
        return tweepy.OAuthHandler(*self.tokens)
    
    def request_url(self, done_url = None):
        auth = self.twitter_auth()
        signin_url    = auth.get_authorization_url()
        return signin_url
        request_token = auth.request_token
        (request_token.key,request_token.secret),auth.get_authorization_url()

    def done(self, djp, key, secret):
        data    = djp.request.GET
        verifier = data.get('oauth_verifier', None)
        auth = self.twitter_auth()
        auth.set_request_token(key,secret)
        try:
            return auth.get_access_token(verifier)
        except:
            return None    


Twitter()




class TwitterPostView(appview.AppView):
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

