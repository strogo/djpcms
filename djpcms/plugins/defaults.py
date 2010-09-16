from django import forms
from djpcms.plugins import DJPplugin
from djpcms.utils.navigation import Navigator

layouts = (
           ('v','vertical'),
           ('o','orizontal')
           )
dlayouts = dict(layouts)

class navigationForm(forms.Form):
    levels = forms.ChoiceField(choices = ((1,1),(2,2)))
    layout = forms.ChoiceField(choices = (('v','vertical'),('o','orizontal')))


class SoftNavigation(DJPplugin):
    '''Display the site navigation from the closest "soft" root for a given number of levels.'''
    name = 'soft-nav'
    description = 'Navigation'
    form = navigationForm
    
    def render(self, djp, wrapper, prefix, levels = 1, layout = 'v', **kwargs):
        nav = Navigator(djp, soft = True, levels = levels, classes = dlayouts[layout])
        return nav.render()