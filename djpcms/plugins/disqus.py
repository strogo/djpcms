from django import forms

from djpcms.plugins import DJPplugin
from django.template import loader
from djpcms.utils import version


class DisqusForm(forms.Form):
    '''
    Form for changing text content during inline editing
    '''
    site = forms.CharField(max_length = 60)
    

class disqusThread(DJPplugin):
    name = 'disqus-thread'
    description = 'DISQUS Thread'
    form = DisqusForm
    
    def render(self, djp, wrapper, prefix, site = None, **kwargs):
        if site:
            a = '''<script type="text/javascript" src="http://disqus.com/forums/%s/embed.js"></script>''' % site
            b = '''<a href="http://disqus.com/forums/%s/?url=ref">View the discussion thread.</a>''' % site
            return '''<div id="disqus_thread"></div>%s<noscript>%s</noscript>''' % (a,b)
        else:
            return ''
