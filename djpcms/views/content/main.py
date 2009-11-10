'''
Battery included content editing views
The main view handle inline content management editing.
'''
from djpcms.ajax import dialog, jhtmls
from djpcms.views import Factory
from djpcms.models import Page, create_new_content

from editcontent import *


class basechild(Factory.childview):
    
    def get_object(self, args):
        try:
            self.position = int(args[0])
            try:
                contents      = self.contentpage.description.split(' ')
                code          = contents[self.position]
                self.object   = SiteContent.objects.get_from_code(code)
            except:
                self.object   = None
        except:
            raise Http404
        
    def __get_contentpage(self):
        return self.parentview.contentpage
    contentpage = property(fget = __get_contentpage)
    

class editview(basechild):
    
    def get_selectform(self, request, data = None):
        return contentselectform(request = request, data = data, view = self, cn = select_form_class)
        
    def get_editform(self, request, data = None, forceadd = False):
        '''
        Content edit form
        '''
        initial = None
        if self.object and not forceadd:
            formtype = EditForm
            if data is None:
                initial = {'body': self.object.body}
            template = 'djpcms/content/edit.html'
        else:
            formtype = AddForm
            template = 'djpcms/content/add.html'
        return editform(request = request,
                        initial = initial,
                        data = data,
                        url = self.url,
                        template = template,
                        formtype = formtype)
        
    def default_post(self, request, params):
        '''
        Return a dialog widget
        '''
        if self.object:
            hd = 'Editing content %s' % self.object.code
            func = 'save_content'
        else:
            hd = 'Add new content'
            func = 'save_new_content'
        form = self.get_editform(request)
        d = dialog(hd = hd,
                   bd = form.render(),
                   modal = True,
                   width = CONTENT_INLINE_EDITING.get('width',500),
                   height = CONTENT_INLINE_EDITING.get('height',400),
                   dialogClass = HTML_CLASSES.site_content_prefix)
        d.addbutton('Ok', url = self.url, func = func)
        if self.object:
            d.addbutton('Save', url = self.url, func = func, close = False)
        return d
    
    def save_new_content(self, request, data):
        return self.save_content(request, data, True)
        
    def save_content(self, request, data, forceadd = False):
        f = self.get_editform(request, data, forceadd)
        if f.is_valid():
            body = f.cleaned_data.get('body')
            code = f.cleaned_data.get('name',None)
            if code:
                self.object = create_new_content(code = code, body = body, user = request.user)
                msg  = 'content %s created' % code
                self.contentpage.set_content(self.position, self.object.code)
            elif self.object:
                self.object.update(user = request.user, body = body)
                msg = 'content saved'
            jhtmls = f.messagepost(msg)
            html = self.object.htmlbody()
            jhtmls.add(identifier = '#%s' % contentid(self.position), html = html, alldocument = True)
            return jhtmls
        else:
            return f.jerrors
        
    def select_content(self, request, data):
        val = data.get('value',None)
        try:
            id = int(val)
        except:
            id = None
        if id:
            if self.object and self.object.id == id:
                return
            self.object = SiteContent.objects.get(id = id)
            html = self.object.htmlbody()
            self.contentpage.set_content(self.position, self.object.code)
            return jhtmls(identifier = '#%s' % contentid(self.position), html = html, alldocument = True)
        else:
            obj = self.object
            self.object = None
            dp = self.default_post(request, None)
            self.object = obj
            return dp
        
        
class deleteview(basechild):
    
    def default_post(self, request, params):
        '''
        delete the content
        '''
        pass


class view(Factory.view):
    edit = Factory.child('edit',  view = editview)
    delete = Factory.child('delete',  view = deleteview)
    
    def get_object(self, args):
        self.contentpage = Page.objects.get(id = int(args[0]))