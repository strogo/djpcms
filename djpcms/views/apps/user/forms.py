from django.forms.util import ErrorList
from django.contrib.auth import forms as authforms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login


from djpcms import forms


class LoginForm(forms.Form):
    '''The login form
    '''
    username   = forms.CharField(min_length=1,max_length=30)
    password   = forms.CharField(min_length=1,max_length=20,widget=forms.PasswordInput)
    next       = forms.CharField(widget=forms.HiddenInput, required = False)

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
            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    login(request, user)
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
    username = forms.CharField(min_length=5,
                               max_length=32,
                               help_text="Minimum of 6 characters in length")
    #username = NewUserName(min_length=5,
    #                       max_length=32,
    #                       help_text="Minimum of 6 characters in length")
    password = forms.CharField(min_length=5,
                               max_length=32,
                               widget=forms.PasswordInput,
                               label=_("Choose a password"),
                               help_text="Minimum of 6 characters in length")
    re_type  = forms.CharField(min_length=6,max_length=32,widget=forms.PasswordInput,label="Re-enter password")
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
    

class ForgotForm(forms.Form):
    your_email = forms.EmailField()
    

class UserChangeForm(forms.ModelForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, numbers and underscores."))
    
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']


class PasswordChangeForm(authforms.PasswordChangeForm):
    
    def __init__(self, instance = None, *args, **kwargs):
        self.instance = instance
        super(PasswordChangeForm,self).__init__(user = instance, *args, **kwargs)
    
