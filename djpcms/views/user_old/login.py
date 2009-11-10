from django.contrib.auth import authenticate, login

from djpcms.settings import HTML_CLASSES
from djpcms.html import quickform, link
from djpcms.ajax import jredirect

from forms import LoginForm
from tools import BaseUser

class view(BaseUser):
    '''
    A Battery included Login view.
    This object can be used to login users
    '''        
    def title(self):
        return 'Sign in to %s' % self.page.site.name
    
    def get_form(self, request, data = None, initial = None):
        '''
        Create the login form. This function can be reimplemented by
        a derived view
        '''
        return quickform(view = self,
                         request = request,
                         form = LoginForm,
                         initial = initial,
                         data = data,
                         submitname  = 'login_user',
                         submitvalue = 'Sign in',
                         cn = HTML_CLASSES.ajax_form)
        
    def get_form_url(self, request):
        url = self.page.get_absolute_url()
        if r.method == 'GET':
            next = request.GET.get("next", None)
            if next != None:
                url = '%s?next=%s' % (url,next)
        return url
    
    def view_contents(self, request, params):
        data = request.GET.copy()
        if request.user.is_authenticated():
            next = data.pop('next','/')
            return self.redirect_to(next)
        c11 = [self.get_form(request, initial = data)]
        forgoturl = self.factoryurl(request,'forgot')
        createurl = self.factoryurl(request,'add')
        if forgoturl:
            c11.append(link(inner = "I forgot my password or username", url = forgoturl))
        if createurl:
            c11.append(link(inner = "Create a new account", url = createurl))
        
        return {'content11': c11}
    
    def login_user(self, request, params):
        '''
        Try to log in
        '''
        f = self.get_form(request,params)
        if f.is_valid():
            error = self.process_login_data(request,f.cleaned_data)
            if not error:
                next = f.cleaned_data.get('next','/')
                return jredirect(url = next)
            else:
                return self.errorpost(error)
        else:
            return f.jerrors
        
    def process_login_data(self, request, data):
        '''
        process login
        '''
        username = data.get('username',None)
        password = data.get('password',None)
        if username and password:
            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    r = request
                    login(r, user)
                    try:
                        r.session.delete_test_cookie()
                    except:
                        pass
                else:
                    return '%s is not active' % username
            else:
                return 'username or password not recognized'
        else:
            return 'username or password not provided'
