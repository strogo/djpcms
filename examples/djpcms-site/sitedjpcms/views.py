from django import http
from django.conf import settings

from socialauth import views
from socialauth.lib import oauthtwitter2 as oauthtwitter

from djpcms.views.appview import AppView


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

    def __init__(self, regex = 'twitter/login/done', splitregex=False, parent = 'home', **kwargs):
        super(TwitterDone,self).__init__(regex = regex, splitregex=splitregex,  parent=parent, **kwargs)
        
    def response(self, djp):
        return views.twitter_login_done(djp.request)