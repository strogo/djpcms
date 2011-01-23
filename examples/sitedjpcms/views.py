from django import http
from django.conf import settings
from djpcms.contrib import messages
from django.contrib.auth import authenticate, login

from socialauth import views
from oauth import oauth
from socialauth.lib import oauthtwitter2 as oauthtwitter

from djpcms.views.appview import AppView


def del_dict_key(src_dict, key):
    if key in src_dict:
        del src_dict[key]


class TwitterLogin(AppView):
    _methods = ('get',)
    
    def __init__(self, regex = 'twitter/login', splitregex=False, parent = 'home', **kwargs):
        super(TwitterLogin,self).__init__(regex = regex, splitregex=splitregex, parent=parent, **kwargs)
        
    def get_response(self, djp):
        request = djp.request
        next = request.GET.get('next', None)
        if next:
            request.session['twitter_login_next'] = next
        done_url = self.appmodel.appviewurl(djp.request, 'twitter_done')
        twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        request_token = twitter.fetch_request_token(callback=done_url)
        request.session['request_token'] = request_token.to_string()
        signin_url = twitter.authorize_token_url(request_token)
        return http.HttpResponseRedirect(signin_url)


class TwitterDone(AppView):

    def __init__(self, regex = 'done', parent = 'twitter_login', **kwargs):
        super(TwitterDone,self).__init__(regex = regex, parent=parent, **kwargs)
        
    def handle_response(self, djp):
        request = djp.request
        request_token = request.session.get('request_token', None)
        verifier = request.GET.get('oauth_verifier', None)
        denied = request.GET.get('denied', None)
        
        # If we've been denied, put them back to the signin page
        # They probably meant to sign in with facebook >:D
        if denied:
            messages.info(request, 'Could not login. Access denied.')
            return http.HttpResponseRedirect(settings.USER_ACCOUNT_HOME_URL)

        # If there is no request_token for session,
        # Means we didn't redirect user to twitter
        if not request_token:
            # Redirect the user to the login page,
            messages.info(request, 'No request token for session. Could not login.')
            return http.HttpResponseRedirect('/')
    
        token = oauth.OAuthToken.from_string(request_token)
    
        # If the token from session and token from twitter does not match
        # means something bad happened to tokens
        if token.key != request.GET.get('oauth_token', 'no-token'):
            messages.info(request, "Token for session and from twietter don't mach. Could not login.")
            del_dict_key(request.session, 'request_token')
            # Redirect the user to the login page
            return http.HttpResponseRedirect('/')
    
        try:
            twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
            access_token = twitter.fetch_access_token(token, verifier)
    
            request.session['access_token'] = access_token.to_string()
            user = authenticate(twitter_access_token=access_token)
        except Exception, e:
            messages.info(request, 'Could not login. %s' % e)
            user = None
      
        # if user is authenticated then login user
        if user:
            login(request, user)
        else:
            # We were not able to authenticate user
            # Redirect to login page
            del_dict_key(request.session, 'access_token')
            del_dict_key(request.session, 'request_token')
            return http.HttpResponseRedirect('/')
    
        # authentication was successful, use is now logged in
        next = request.session.get('twitter_login_next', None)
        if next:
            del_dict_key(request.session, 'twitter_login_next')
            return http.HttpResponseRedirect(next)
        else:
            home = '%s%s' % (settings.USER_ACCOUNT_HOME_URL,user.username)
            return http.HttpResponseRedirect(home)
        
        