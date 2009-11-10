from django import forms

from djpcms.models import SiteContent
from djpcms.html import box, UniqueCodeField



class cache(object):
    
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.cache = None
        self.tuples = None
        
    def contents(self):
        if not self.cache:
            ca = {}
            cs = SiteContent.objects.all()
            for c in cs:
                ca[c.code] = c.object
            self.cache = ca
        return self.cache
    
    def ctuples(self):
        tu = self.tuples
        if not tu:
            tu = []
            ca = self.contents()
            for c in ca:
                tu.append((c,c))
            self.tuples = tuple(tu)
        return self.tuples


class edit_content_widget(object):
    '''
    Editing a content element
    '''
    cache = cache()
    
    def __init__(self, view, code):
        self.content = self.get_object(code)
        self.editurl = 0
        #form = self.get_form(code)
        #self.html = box(bd = form.as_table(), cn = 'editing')
        
    def get_object(self, code):
        contents = self.__class__.cache.contents()
        return contents[code]
        
    def get_form(self, code):
        content  = get_object(code)
        initial = {'contents':code, 'text': content.body}
        return ContentForm(initial = {'contents':code, 'text': content.body})

        
            


class ContentForm(forms.Form):
    new_content = UniqueCodeField(model = SiteContent, required = False)
    contents    = forms.ChoiceField(choices = edit_content_widget.cache.ctuples())
    text        = forms.CharField(widget = forms.Textarea)

    