from djpcms.contrib import messages
from djpcms.views import appview
from djpcms.utils.ajax import jredirect
from djpcms.forms import saveform
from djpcms.apps.included.user.user import UserClass

from forms import LoginForm, PasswordChangeForm


class LogoutView(appview.ModelView):
    '''
    Logs out a user, if there is an authenticated user :)
    '''
    _methods = ('get',)
    
    def __init__(self, regex = 'logout', parent = None):
        super(LogoutView,self).__init__(regex = regex, parent = parent, isapp = False, insitemap = False)
        
    def preget(self, djp):
        request = djp.request
        params  = dict(request.GET.items())
        url     = params.get('next',None) or '/'
        user    = request.user
        if user.is_authenticated():
            UserClass().logout(request)
        return djp.http.HttpResponseRedirect(url)



class LoginView(appview.ModelView):
    '''A Battery included Login view.
    '''
    def __init__(self, regex = 'login', parent = None, insitemap = False, isplugin = True,
                 form = LoginForm, form_withrequest = True, **kwargs):
        super(LoginView,self).__init__(regex = regex, parent = parent,
                                      insitemap = insitemap,
                                      isplugin = isplugin,
                                      form = form, form_withrequest = form_withrequest,
                                      **kwargs)
        
    def title(self, page, **kwargs):
        if page:
            return 'Sign in to %s' % page.site.name
        else:
            return 'Sign in'
    
    def preget(self, djp):
        if djp.request.user.is_authenticated():
            return djp.http.HttpResponseRedirect('/')
        
    def render(self, djp):
        if djp.request.user.is_authenticated():
            return ''
        else:
            return self.get_form(djp).render(djp)
    
    def default_post(self, djp):
        return saveform(djp, force_redirect = True)
    
    def save(self, request, f):
        return f.cleaned_data['user']
    
    def success_message(self, instance, mch):
        return ''
