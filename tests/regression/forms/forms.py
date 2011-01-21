from djpcms import forms

__all__ = ['LoginForm']


LoginForm = forms.Factory(
                          forms.CharField('username',max_length=60),
                          forms.CharField('password',max_length=60)
                          )


LoginForm2 = forms.Factory(
                           forms.CharField('username',max_length=60),
                           forms.CharField('password',max_length=60),
                           layout = forms.UniForm()
                           )