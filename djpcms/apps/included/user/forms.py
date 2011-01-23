
from django.forms.util import ErrorList
from django.contrib.auth import forms as authforms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login

from djpcms import forms
from djpcms.apps.included.user import UserClass


class LoginForm(forms.Form):
    '''The Standard login form
    '''
    username   = forms.CharField(max_length=30,
                                 widget=forms.TextInput(attrs={'class':'autocomplete-off'}))
    password   = forms.CharField(max_length=60,widget=forms.PasswordInput)

    submits = (('Sign in','login_user'),)
    
    def clean(self):
        '''process login
        '''
        data = self.cleaned_data
        request = self.request
        msg  = ''
        username = data.get('username',None)
        password = data.get('password',None)
        if username and password:
            user = UserClass().authenticate(username = username, password = password)
            if user is not None and user.is_authenticated():
                if user.is_active():
                    user.login(request)
                    try:
                        request.session.delete_test_cookie()
                    except:
                        pass
                    data['user'] = user
                    return data
                else:
                    msg = '%s is not active' % username
            else:
                msg = 'username or password not recognized'
        else:
            return data
        raise forms.ValidationError(msg)
    

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=32)
    #username = NewUserName(min_length=5,
    #                       max_length=32,
    #                       help_text="Minimum of 6 characters in length")
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    re_type  = forms.CharField(max_length=32, widget=forms.PasswordInput,label="Re-enter password")
    #email_address = UniqueEmail(help_text="This will be used for confirmation only.")
    
    def clean(self):
        data     = self.cleaned_data
        password = data.get("password")
        re_type  = data.get("re_type")
        if password != re_type:
            self._errors["re_type"] = ErrorList(["Passwords don't match. Please try again."])
            try:
                del data["re_type"]
            except:
                pass
        return data
    

#class ForgotForm(forms.Form):
#    your_email = forms.EmailField()
    

class PasswordChangeForm(forms.Form):
    
    def __init__(self, instance = None, save_as_new=False, *args, **kwargs):
        self.instance = instance
        super(PasswordChangeForm,self).__init__(user = instance, *args, **kwargs)
    
