from django import http
from djpcms.contrib import messages

from djpcms import forms
from djpcms.utils.uniforms import FormLayout, Fieldset, nolabel
from djpcms.views import appview
from djpcms.utils.ajax import jerror, jhtmls

from flowrepo import settings
from flowrepo.models import LinkedAccount
from flowrepo.cms.views import LinkedAccountLoginView

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


def twitter_auth(key = None, secret = None, **kwargs):
    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_TOCKEN, settings.TWITTER_CONSUMER_SECRET)
    if key and secret:
        auth.set_access_token(key, secret)
    return auth


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


class TwitterLogin(LinkedAccountLoginView):
    provider = 'twitter'
    _methods = ('get',)
    
    def __init__(self, regex = 'twitter/login', splitregex=False, parent = 'home', **kwargs):
        super(TwitterLogin,self).__init__(regex = regex, splitregex=splitregex, parent=parent, **kwargs)
        
    def get_response(self, djp):
        request = djp.request
        next = request.GET.get('next', None)
        if next:
            request.session['twitter_login_next'] = next
        done_url = self.appmodel.appviewurl(request, 'twitter_done')
        auth = twitter_auth()
        signin_url    = auth.get_authorization_url()
        request_token = auth.request_token
        request.session['request_token'] = (request_token.key,request_token.secret)
        return http.HttpResponseRedirect(signin_url)


class TwitterDone(appview.AppView):

    def __init__(self, regex = 'done', parent = 'twitter_login', **kwargs):
        super(TwitterDone,self).__init__(regex = regex, parent=parent, **kwargs)
        
    def handle_response(self, djp):
        request = djp.request
        session = request.session
        data    = request.GET
        request_token = session.get('request_token', None)
        del_dict_key(request.session, 'request_token')
        verifier = data.get('oauth_verifier', None)
        
        # If we've been denied, put them back to the signin page
        # They probably meant to sign in with facebook >:D
        if data.get('denied', None):
            messages.info(request, 'Could not login. Access denied.')
            return http.HttpResponseRedirect(settings.USER_ACCOUNT_HOME_URL)

        # If there is no request_token for session,
        # Means we didn't redirect user to twitter
        if not request_token:
            # Redirect the user to the login page,
            messages.info(request, 'No request token for session. Could not login.')
            return http.HttpResponseRedirect('/')
    
        key,secret = request_token
    
        # If the token from session and token from twitter does not match
        # means something bad happened to tokens
        if key != request.GET.get('oauth_token', 'no-token'):
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
        
        