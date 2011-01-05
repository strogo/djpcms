from copy import copy
import logging
from datetime import datetime

import djpcms
import djpcms.contrib.social.providers
from djpcms.plugins import DJPplugin, get_plugin
from djpcms.contrib import messages
from djpcms.views import appview
from djpcms.template import loader
from djpcms.utils.ajax import jpopup
from djpcms.views.decorators import deleteview
from djpcms.contrib.social import provider_handles
from djpcms.contrib.social.models import LinkedAccount
from djpcms.apps.included.user import UserApplication

from django.contrib.auth import authenticate, login

from .defaults import User


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
            p = djp.kwargs.get('provider',None)
            if p:
                raise djp.http.Http404('Provider {0} not available'.format(p))
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
            for provider in providers.values():
                vdjp = loginview(djp, provider = provider)
                clsname  = None if not provider.auth_popup else djp.css.ajax
                tolink.append({'name':provider, 'url':vdjp.url, 'class':clsname})
                    
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
    _methods = ('get','post')
    
    def get_response(self, djp):
        return self._handle(djp)
    
    def default_post(self, djp):
        return self._handle(djp)

    def _handle(self, djp):
        provider = self.provider(djp)
        request  = djp.request
        http     = djp.http
        
        if not provider:
            raise http.Http404
    
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
            
        uri = djpcms.get_url(User, 'social_done', provider = provider)
        if uri:
            uri = '%s://%s%s' % ('https' if request.is_secure() else 'http', request.get_host(), uri)
        
        rtoken = provider.fetch_request_token(uri)
        
        referer_url = request.environ.get('HTTP_REFERER') or '/'
        url = provider.fetch_authentication_uri(rtoken)
        
        if rtoken:
            request.session['request_token'] = rtoken.key,rtoken.secret,referer_url
        else:
            request.session['request_token'] = None,None,referer_url
            
        if request.is_ajax():
            return jpopup(url)
        else:
            return http.HttpResponseRedirect(url)
    

class SocialLoginDoneView(SocialView):
    '''View which handle the callback frpm the AOuth provider'''
    _methods = ('get',)
    
    def get_response(self, djp):
        provider = self.provider(djp)
        http = djp.http
        if provider:
            request = djp.request
            session = request.session
            data    = dict(request.GET.items())
            
            try:
                key, secret, refer_url = session.pop('request_token', None)
            except:
                # Redirect the user to the login page,
                messages.error(request, 'No request token for session. Could not login.')
                return http.HttpResponseRedirect('/')
            
            access_token = provider.quick_access_token(data)
            
            if not access_token:
                
                if data.get('denied', None):
                    messages.info(request, 'Could not login. Access denied.')
                    return http.HttpResponseRedirect(djp.settings.USER_ACCOUNT_HOME_URL)
                
                oauth_token = data.get('oauth_token', None)
                oauth_verifier = data.get('oauth_verifier', None)
                    
                if not oauth_token:
                    messages.error(request, "{0} authorization token not available.".format(provider))
                    return http.HttpResponseRedirect(refer_url)
                
                if key != oauth_token:
                    messages.error(request, "{0} authorization token and session token don't mach.".format(provider))
                    return http.HttpResponseRedirect(refer_url)
                
                rtoken = provider.authtoken(key,secret,oauth_verifier)
                
                try:
                    access_token = provider.access_token(rtoken)
                    if not access_token:
                        messages.error(request, "Coud not obtain access token")
                        return http.HttpResponseRedirect(refer_url)
                except Exception as e:
                    messages.error(request, "Coud not obtain access token. {0}".format(e))
                    return http.HttpResponseRedirect(refer_url)
            
            self.create_or_update_user(request, provider, access_token)
            
            # authentication was successful, use is now logged in
            next = session.pop('%s_login_next' % provider, refer_url)
            res = http.HttpResponseRedirect(next)
            res.set_cookie(provider.cookie(),provider.get_access_token_key(access_token))
            return res
        else:
            raise http.Http404
        
    
    def create_or_update_user(self, request, provider, access_token):
        response, access_token_key, access_token_secret = provider.user_data(access_token)
        user = authenticate(provider = provider,
                            token = access_token_key,
                            secret = access_token_secret,
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
        return djp.site.getapp('account-social_action')
        
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
    
    