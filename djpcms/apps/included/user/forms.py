from djpcms import sites, forms


class LoginForm(forms.Form):
    '''The Standard login form
    '''
    username   = forms.CharField(max_length=30,
                                 widget=forms.TextInput(cn = 'autocomplete-off'))
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
        User = sites.User
        if not User:
            raise forms.ValidationError('No user')
        user = User.authenticate(username = username, password = password)
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
        raise forms.ValidationError(msg)
    

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=32)
    password = forms.CharField(max_length=32,
                               widget=forms.PasswordInput)
    re_type  = forms.CharField(max_length=32,
                               widget=forms.PasswordInput,
                               label="Re-enter password")
    #email_address = UniqueEmail(help_text="This will be used for confirmation only.")
    
    def clean(self):
        data     = self.cleaned_data
        password = data.get("password")
        re_type  = data.get("re_type")
        if password != re_type:
            self._errors["re_type"] = forms.List(data=["Passwords don't match. Please try again."],
                                                 cn=sites.settings.HTML_CLASSES.errorlist)
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
    
