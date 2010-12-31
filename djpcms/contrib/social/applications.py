from copy import copy
import logging
from datetime import datetime

from djpcms.conf import settings
import djpcms.contrib.social.providers
from djpcms import http, get_site
from djpcms.plugins import DJPplugin, get_plugin
from djpcms.contrib import messages
from djpcms.views import appview
from djpcms.template import loader
from djpcms.views.apps.user import UserApplication
from djpcms.views.decorators import deleteview
from djpcms.contrib.social import provider_handles, client
from djpcms.contrib.social.models import LinkedAccount

from django.contrib.auth import authenticate, login


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
            return ''
        provider = self.provider(djp)
        if not provider:
            return self.render_all(djp)
        else:
            return ''
        
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
        provider = self.provider(djp)
        if not provider:
            raise http.Http404
    
        request  = djp.request
        user     = request.user
        next     = request.GET.get('next', None)
        
        # User may be authenticated, In which case we see if it has already the account linked.
        if user.is_authenticated():
            if authenticate(provider = provider, user = user) == user:
                return http.HttpResponseRedirect(next)
            
        sname  = provider.cookie()
        key    = request.COOKIES.get(sname,None)
        if next:
            request.session['%s_login_next' % provider] = next
        if key and not user.is_authenticated():
            user = authenticate(provider = provider, token = key)
            if user:
                if user.is_active:
                    login(request, user)
                return http.HttpResponseRedirect(next)
            
        utoken = provider.unauthorized_token(request)
        return provider.authenticate(request, utoken)
    

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
                messages.error(request, 'No request token for session. Could not login.')
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
            
            rtoken = provider.authtoken(request_token)
            access_token = provider.access_token(request, rtoken)
            
            if not access_token:
                return http.HttpResponseRedirect('/')
            
            self.create_or_update_user(request, provider, access_token)
            
            # authentication was successful, use is now logged in
            next = session.pop('%s_login_next' % provider, None)
            if next:
                res = http.HttpResponseRedirect(next)
            else:
                res = http.HttpResponseRedirect(settings.USER_ACCOUNT_HOME_URL)
            sname  = provider.cookie()
            res.set_cookie(sname,access_token.key)
            return res
        else:
            raise http.Http404
        
    
    def create_or_update_user(self, request, provider, access_token):
        response = provider.user_data(request, access_token)
        user = authenticate(provider = provider,
                            token = access_token.key,
                            secret = access_token.secret,
                            response = response,
                            user = request.user)
        if user and user.is_active:
            login(request, user)
        return user
    
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
            

class SocialActionView(SocialView):
    
    def get_auth(self, djp):
        user = djp.request.user
        if user.is_authenticated() and user.is_active:
            provider = self.provider(djp)
            social = user.linked_accounts.filter(provider = str(provider))
            if social:
                social = social[0]
            else:
                return None
            return provider.authtoken((social.token,social.secret))
    
    def default_post(self, djp):
        user = djp.request.user
        if user.is_authenticated() and user.is_active:
            provider = self.provider(djp)
            social = user.linked_accounts.filter(provider = str(provider))
            if social:
                social = social[0]
            else:
                return self.error_post('Could not authenticate user')
                
            name = '{0}/{1}'.format(provider,djp.getdata('action'))
            plugin = get_plugin(name)
            if not plugin:
                return self.error_post('Could not find plugin {0}'.format(name))
            api  = provider.authenticated_api(social.token,social.secret)
            return plugin.handle_post(djp, api, social)

    def error_post(self, djp, msg):
        if djp.request.is_ajax():
            return jerror(msg)
        else:
            return self.handle_response(djp)


def deletesocial(djp):
    c = client(djp.request.user,getprovider(djp))
    c.delete()
        

class SocialUserApplication(UserApplication):
    '''Extend user application with AOUTH and social actions'''
    inherit = True
    name          = 'account'
    social_home   = SocialView(regex = '(?P<provider>[-\.\w]+)',
                               parent = 'home',
                               isplugin = True)
    social_login  = SocialLoginView(regex = 'login', parent = 'social_home')
    social_done   = SocialLoginDoneView(regex = 'done', parent = 'social_login')
    social_delete = deleteview(deletesocial, parent = 'social_home')
    social_action = SocialActionView(regex = '(?P<action>[-\.\w]+)',
                                     parent = 'social_home',
                                     isapp = False,
                                     isplugin = False,
                                     form_withrequest = True,
                                     form_ajax = True)
    

class SocialActionPlugin(DJPplugin):
    provider_name = None
    action_name = None
    
    def get_view(self, djp):
        site = get_site(djp.request.path)
        return site.getapp('account-social_action')
        
    def render(self, djp, wrapper, prefix, **kwargs):
        view = self.get_view(djp)
        viewdjp = view(djp.request, provider = self.provider_name, action = self.action_name)
        return self._render(viewdjp)
    
    def _render(self, djp):
        return ''
        
    def _register(self):
        if self.action_name and self.provider_name:
            self.name = '{0}/{1}'.format(self.provider_name,self.action_name)
            super(SocialActionPlugin,self)._register()
    
    