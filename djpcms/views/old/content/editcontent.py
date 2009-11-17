from django import forms

from djpcms.settings import CONTENT_INLINE_EDITING, HTML_CLASSES
from djpcms.views import site
from djpcms.html import SlugField, form, formlet, div, AjaxModelChoice2
from djpcms.models import SiteContent


select_form_class = 'content-select'



def contentid(pos):
    return '%s-%s' % (HTML_CLASSES.site_content_prefix,pos)


def baseurl(page):
    '''
    Calculate the url for editing a sitecontent.
        @param pos: integer content positioning in the page
        @param page: instance of Page
    '''
    if CONTENT_INLINE_EDITING.get('available',False):
        baseurl = CONTENT_INLINE_EDITING.get('pagecontent')
        return '/%s/%s/' % (baseurl,page.id)
    else:
        return None


def contenteditview(request, pos, page):
    url = '%sedit/%s/' % (baseurl(page),pos)
    return site.handle_page(request,url[1:-1])

def contentdeleteview(request, pos, page):
    url = '%sdelete/%s/' % (baseurl(page),pos)
    return site.handle_page(request,url[1:-1])

class EditForm(forms.Form):
    body = forms.CharField(widget = forms.Textarea)
    
class AddForm(forms.Form):
    name = SlugField(SiteContent,'code', help_text="Unique name for content. Choose one you like.")
    body = forms.CharField(widget = forms.Textarea)
    
    

class ContentSelect(forms.Form):
    select_content = AjaxModelChoice2(queryset = SiteContent.objects.all(),
                                      required = False,
                                      empty_label = 'Create New Content',
                                      label    = 'content')
    

    
class editform(form):
    
    def __init__(self, *args, **kwargs):
        self.formtype = kwargs.pop('formtype',None)
        super(editform,self).__init__(*args, **kwargs)
        
    def addnew(self):
        return self.formtype == AddForm
    
    def _make(self, data = None, initial = None, *args, **kwargs):
        co = self.make_container()
        co['edit'] = formlet(form     = self.formtype,
                             data     = data,
                             initial  = initial,
                             url      = self.url,
                             request  = self.request,
                             template = self.template)

class contentselectform(form):
    
    def __init__(self, *args, **kwargs):
        super(contentselectform,self).__init__(*args, **kwargs)
        
    def _make(self, data = None, initial = None, *args, **kwargs):
        if self.object and not data:
            initial = {'select_content':self.object.id}
        self['edit'] = formlet(form     = ContentSelect,
                               data     = data,
                               initial  = initial,
                               url      = self.url,
                               request  = self.request,
                               layout   = 'flat')    