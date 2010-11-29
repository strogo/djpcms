import logging
from datetime import datetime

from django import http
from django.contrib import messages
from django.contrib.auth import authenticate

from djpcms.conf import settings
import djpcms.contrib.social.providers
from djpcms.views import appview
from djpcms.template import loader
from djpcms.views.apps.user import UserApplication
from djpcms.views.decorators import deleteview
from djpcms.contrib.social import provider_handles, client
from djpcms.contrib.social.models import LinkedAccount


def getprovider(djp):
    return provider_handles.get(djp.kwargs.get('provider',None),None)       


class SocialView(appview.ModelView):
    '''Model View class for handling social providers'''
    
    def provider(self, djp):
        '''Extract provider from url if available. Return and instance of
:model:`djpcms.contrib.social.SocialProvider` or ``None``.'''
        return provider_handles.get(djp.kwargs.get('provider',None),None)        
    
    def render(self, djp):
        user = djp.request.user
        if not user.is_authenticated() or not user.is_active:
            return u''
        provider = self.provider(djp)
        if not provider:
            return self.render_all(djp)
        else:
            pass
        
    def render_all(self, djp):
        '''Render all linked and non-linked providers'''
        user = djp.request.user
        accounts = user.linked_accounts.all()
        linked = []
        tolink = []
        providers = provider_handles.copy()
        
        for account in accounts:
            providers.pop(account.provider,None)
            linked.append({'name':account.provider})
        
        loginview = self.appmodel.getview('social_login')
        if loginview:
            for provider in providers:
                vdjp = loginview(djp, provider = provider)
                tolink.append({'name':provider, 'url':vdjp.url})
                    
        c = {'accounts':accounts,
             'url': djp.request.path,
             'linked': linked,
             'tolink':tolink}
        return loader.render_to_string('social/linked_accounts.html', c)
    
    def get_account_to_link(self, djp, accounts):
        appmodel = self.appmodel
        
        for view in appmodel.views.itervalues():
            if isinstance(view,SocialLoginView):
                if not accounts.filter(provider = view.provider):
                    vdjp = view(djp)
                    yield {'name':view.provider, 'url':vdjp.url}


class SocialLoginView(SocialView):
    _methods = ('get',)
    
    def get_response(self, djp):
        request = djp.request
        provider = self.provider(djp)
        dview = self.appmodel.getview('social_done')
        if provider and dview:
            utoken = provider.unauthorized_token(request)
            request = djp.request
            next = request.GET.get('next', None)
            if next:
                request.session['%s_login_next' % provider] = next
            path = dview(djp, **djp.kwargs).url
            callback_url = '%s://%s%s' % ('https' if request.is_secure() else 'http', request.get_host(), path)
            request_token,signin_url = provider.request_url(djp, callback_url = callback_url)
            request.session['request_token'] = request_token
            return http.HttpResponseRedirect(str(signin_url))
        else:
            raise http.Http404
    

class SocialLoginDoneView(SocialView):
    '''View which handle the callback frpm the AOuth provider'''
    _methods = ('get',)
    
    def get_response(self, djp):
        provider = self.provider(djp)
        if provider:
            request = djp.request
            session = request.session
            data    = request.GET
            request_token = session.pop('request_token', None)
            
            if not request_token:
                # Redirect the user to the login page,
                messages.info(request, 'No request token for session. Could not login.')
                return http.HttpResponseRedirect('/')
            
            if data.get('denied', None):
                messages.info(request, 'Could not login. Access denied.')
                return http.HttpResponseRedirect(settings.USER_ACCOUNT_HOME_URL)
            
            oauth_token = data.get('oauth_token', 'no-token')
            key,secret = request_token
            
            if key != oauth_token:
                messages.info(request, "Token for session and from %s don't mach. Could not login." % provider)
                # Redirect the user to the login page
                return http.HttpResponseRedirect('/')
            
            access_token = provider.done(djp, key, secret)
            
            if not access_token:
                return http.HttpResponseRedirect('/')
            
            user = request.user
            if not user.is_authenticated():
                self.create_user(provider, access_token)
            else:
                self.update_user(user, provider, access_token)
            
            # authentication was successful, use is now logged in
            next = session.pop('%s_login_next' % provider, None)
            if next:
                return http.HttpResponseRedirect(next)
            else:
                return http.HttpResponseRedirect(settings.USER_ACCOUNT_HOME_URL)
        else:
            raise http.Http404
        
    
    def create_user(self, provider, token):
        user = authenticate(provider = provider, token = token.key, secret = token.secret)
    
    def update_user(self, user, provider, token):
        acc  = user.linked_accounts.filter(provider = str(provider))
        if acc:
            acc = acc[0]
            if acc.token != token.key:
                acc.token = token.key
                acc.secret = token.secret
                acc.token_date = datetime.now()
                acc.save()
        else:
            acc = LinkedAccount(user = user, provider = str(provider), token_date = datetime.now(),
                                token = token.key, secret = token.secret)
            acc.save()
        return acc
            

class SocialActionView(appview.ModelView):
    pass


def deletesocial(djp):
    c = client(djp.request.user,getprovider(djp))
    c.delete()
        



class SocialUserApplication(UserApplication):
    inherit = True
    social_home   = SocialView(regex = '(?P<provider>[-\.\w]+)', parent = 'home', isplugin = True)
    social_login  = SocialLoginView(regex = 'login', parent = 'social_home')
    social_done   = SocialLoginDoneView(regex = 'done', parent = 'social_login')
    social_delete = deleteview(deletesocial, parent = 'social_home')
    social_action = SocialActionView(regex = '(?P<action>[-\.\w]+)',
                                     parent = 'social_home',
                                     isapp = False,
                                     isplugin = True,
                                     form_withrequest = True,
                                     form_ajax = True)
    