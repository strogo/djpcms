import os
import copy

from django import forms, http
from django.conf.urls.defaults import url

from djpcms.views import appsite, appview
from djpcms.views.user import LoginApp, LogoutApp
from djpcms.plugins import register_application
from djpcms.plugins import ApplicationPlugin
from djpcms.template import loader

from providers import providers


class OAuthSelection(forms.Form):
    selection = forms.MultipleChoiceField(choices = providers.choices(), required = True)


class OAuthPlugin(ApplicationPlugin):
    form = OAuthSelection
    
    def render(self, djp, wrapper, prefix, selection = None, **kwargs):
        '''
        This function needs to be implemented
        '''
        app  = self.app
        args = copy.copy(djp.urlargs)
        args.update(kwargs)
        instance = args.pop('instance',None)
        if instance and not isinstance(instance,app.model):
            instance = None 
        ndjp = self.app(djp.request, instance = instance, **args)
        ndjp.wrapper = wrapper
        ndjp.prefix  = prefix
        return self.app.render(ndjp)
    
    def css(self):
        f = open(os.path.join(os.path.dirname(__file__),'media/oauth.css'))
        return f.read()


class OAuthLogin(LoginApp):
    '''
    login pannel with multiple authentication via OAuth
    http://oauth.net/
    '''
    form = OAuthSelection
    
    def get_plugin(self):
        return OAuthPlugin(self)
    
    def hasdata(self, djp):
        return djp.request.method == 'POST'
    
    def render(self, djp, selection = None, **kwargs):
        request = djp.request
        if request.user.is_authenticated():
            return ''
        if request.method == 'POST':
            pass
        else:
            #f = self.get_form(djp)
            #return f.render()
            return loader.render_to_string(['oauth.html',
                                            'authentication/oauth.html'],
                                           {'items': providers.list,
                                            'url': djp.url})
    
    def default_post(self, djp):
        request = djp.request
        provider = djp.urlargs.get('provider')
        if not provider:
            items = dict(request.POST.items())
            provider = items.get('provider',None)
        if not provider:
            raise ValueError("Provider not available")
        p = providers.get(provider)
        if not p:
            raise ValueError("Provider %s not available" % p)
        f = p.Login(request.POST)
        if f.is_valid():
            res = p.process(request, **f.cleaned_data)
            if isinstance(res,http.HttpResponse):
                return res


class OAuthDone(LoginApp):
    
    def default_post(self, djp):
        request = djp.request
        items = dict(request.POST.items())
        provider = items.get('provider',None)
        if not provider:
            raise ValueError("Provider not available")
        p = providers.get(provider)
        if not p:
            raise ValueError("Provider %s not available" % p)
        f = p.Login(request.POST)
        if f.is_valid():
            res = p.process(request, **f.cleaned_data)
            if isinstance(res,http.HttpResponse):
                return res
            



class OAuthApplication(appsite.ModelApplication):
    '''
    OAuth authentication application
    '''
    name           = 'oauth'
    home           = appview.AppView()
    login          = OAuthLogin(regex = 'login', parent = 'home', isplugin = True)
    login_provider = OAuthLogin(regex = '(?P<provider>\w+)', parent = 'login', isplugin = False)
    login_done     = OAuthDone(regex = 'done', parent = 'login_provider', isplugin = False)
    logout         = LogoutApp(parent = 'home')

