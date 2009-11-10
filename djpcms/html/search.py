from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.text import truncate_html_words

from base import TemplatePlugin, div
from form import form, formlet, submit

__all__ = ['searchform','searchentry']


class SearchForm(forms.Form):
    '''
    A simple search box
    '''
    search = forms.CharField(max_length=300, required = False,
                             widget = forms.TextInput(attrs={'class':'search-box'}))


class searchform(form):
    _form = SearchForm
    '''
    A search form plugin.
    This plugin display a serch widget a-la google
    '''
    def __init__(self, **attrs):
        super(searchform,self).__init__(**attrs)
        
    def _make(self, data = None, **kwargs):
        co = self.make_container(div, cn = self.ajax.search_entry)
        co['search']  = formlet(form     = self._form,
                                data     = data,
                                layout   = 'flat-notag',
                                submit = submit(value = 'Search', name = 'process_data'))
        co['extra'] = self.extraforms(data)
        
    def extraforms(self,data):
        return None
    
    
class searchentry(TemplatePlugin):
    '''
    HTML plug-in which render a search result.
    This component can be derived to target specific display needs
        withedit    -    If true an edit link will be displayed
        withdelete  -    If true a delete link will be displayed
    '''
    def __init__(self, withedit = True, withdelete = True, **kwargs):
        self.max_words = kwargs.pop('max_words',50)
        obj            = self.object
        view           = self.view
        if withedit:
            self.editurl   = view.safeurl(view.editview(self.request, obj))
        else:
            self.editurl   = None
        if withdelete:
            self.deleteurl   = view.safeurl(view.deleteview(self.request,obj))
        else:
            self.deleteurl   = None
        self.viewurl   = view.safeurl(view.viewview(self.request,obj))
        self.header    = force_unicode(obj)
        if not self.template:
            self.template = 'djpcms/components/search_result_item.html'
            
    def wrap_internal_widget(self, el):
        return el
        
    def description(self):
        if self.max_words:
            des = truncate_html_words(self.object.description, self.max_words)
        else:
            des = self.object.description
        return mark_safe(force_unicode(des))
    
        
