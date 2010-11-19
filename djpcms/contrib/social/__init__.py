from django import http
from django.contrib import messages

provider_handles = {}


class SocialProvider(object):
    
    def __init__(self):
        self.name = self.__class__.__name__.lower()
        from djpcms.conf import settings
        consumers = getattr(settings,'SOCIAL_OAUTH_CONSUMERS',None)
        if consumers:
            consumers = consumers.get(self.name,None)
        if consumers:
            self.tokens = consumers
            provider_handles[self.name] = self
            
    def __str__(self):
        return self.name
    
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