from django import forms

from djpcms.template import loader
from djpcms.plugins import DJPplugin



class TwitterSearchForm(forms.Form):
    search = forms.CharField()
    subject = forms.CharField()
    caption = forms.CharField(required = False)
    width = forms.IntegerField(initial = 250)
    height = forms.IntegerField(initial = 300)
    border_background = forms.CharField(initial = '#4E4D4A')
    border_color = forms.CharField(initial = '#fff')
    background = forms.CharField(initial = '#fff')
    color = forms.CharField(initial = '#444444')
    links_color = forms.CharField(initial = '#1985b5')
    

class TwitterSearch(DJPplugin):
    form = TwitterSearchForm
    
    def render(self, djp, wrapper, prefix, **kwargs):
        return loader.render_to_string('djpcms/bits/twittersearch.html', kwargs)