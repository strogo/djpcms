from django.utils.encoding import force_unicode
from django import forms

from djpcms.utils.ajax import jhtmls, jerrors, jredirect
from djpcms.utils.func import slugify, isforminstance

from base import htmlPlugin, compactTag, TemplatePlugin, div
from shortcuts import submit
from boundfield import BoundField

__all__ = ['form','formlet','formmodel','quickform']



class form(htmlPlugin):
    tag = 'form'
    
    def __init__(self, **attrs):
        self.attrs['method'] = attrs.pop('method','post')
        self.attrs['action'] = self.url or '.'
        self.jerrors   = None
        self._make(**attrs)
        
    def _make(self, **attrs):
        pass
        
    def make_container(self, co = None, **attrs):
        self['errors']    = div(cn = self.ajax.ajax_server_error)
        self['messages']  = div(cn = self.ajax.formmessages)
        if co:
            self['container'] = co(**attrs)
            return self.container
        else:
            return self
    
    def messagepost(self, html):
        return jhtmls(html = html, identifier = '.%s' % self.ajax.formmessages)
    
    def errorpost(self, html):
        '''
        a form error message
        '''
        ehtml = u'\n'.join(['<div class="form-error">',html,'</div>'])
        return self.messagepost(ehtml)
    
    def redirect(self, url):
        return jredirect(url)
    
    def is_valid(self):
        '''
        Check if form is valid. If not fill the ajaxerrors dictionary
        '''
        flets = self.getplugins(formlet)
        self.jerrors = jerrors()
        errs  = self.jerrors
        valid = True
        self.cleaned_data = {}
        for flet in flets:
            if not flet.is_valid():
                errs.update(flet.jerrors)
                valid = False
            else:
                self.cleaned_data.update(flet.cleaned_data)
        return valid
    
    def save(self, *args):
        flets = self.getplugins(formlet)
        id = None
        for flet in flets:
            id_ = flet.save(*args)
            if id_:
                id = id_
        return id
        

   
class fieldhandle(object):
    
    def __init__(self, flet):
        self.flet = flet
    
    def __getattr__(self, fname):
        form = self.flet.form
        bf   = form[fname]
        if bf:
            b = BoundField(bf,self.flet)
            return b
        else:
            return None
    
        

class formlet(TemplatePlugin):
    '''
    Plugin which wrap a django form.
    This wrapper is purely for convenience
    '''
    def __init__(self, prefix = None, **attrs):
        '''
        Initialize the formlet.
            layout:    The layout when rendering the form
                        onecolumn:   render as 1 column table
                        twocolumns:  render as a 2 columns table (default)
                        flat:        render as one row
                        custom:      custom template
        '''
        if self.template is None:
            layout = attrs.pop('layout','twocolumns')
            if layout == 'onecolumn':
                self.template = 'djpcms/form/onecolumnformlet.html'
            elif layout == 'flat':
                self.template = 'djpcms/form/inlineformlet.html'
            elif layout == 'flat-notag':
                self.template = 'djpcms/form/inlineformlet_notag.html'
            elif layout == 'threecolumns':
                self.template = 'djpcms/form/threecolumnformlet.html'
            else:
                self.template = 'djpcms/form/formlet.html'
            self.addclass(layout)
            
        fo = attrs.pop('form',None)
        
        if isforminstance(fo):
            self.form = fo
        else:
            self.form_class = fo 
            kw = {}
            files = attrs.pop('files',None)
            if files is not None:
                kw['files'] = files
            data = attrs.pop('data',None)
            if data:
                kw['data'] = data
            kw['initial']   = attrs.pop('initial',None)
            self.__prefix   = None
            if prefix != None:
                self.__prefix  = str(prefix)
            self.handledata(**kw)
        
        if self.form:
            self.handle = fieldhandle(self)
            
        self.jerrors    = None
        
        submit = attrs.pop('submit',None)
        if submit != None:
            if not isinstance(submit,list):
                submit = [submit]
            for s in submit:
                self[s.attrs['name']] = s
        
    def handledata(self, **kw):
        if self.form_class:
            request = self.request
            if self.object:
                kw['instance'] = self.object
            f = None
            if request:
                try:
                    f = self.form_class(request = request, prefix = self.__prefix, **kw)
                except TypeError:
                    f = None
            if f == None:
                f = self.form_class(prefix = self.__prefix, **kw)
            self.form   = f
        else:
            self.form = []
        
    def __get_fields(self):
        if self.form:
            return self.form.fields
        else:
            return []
    fields = property(fget = __get_fields)
    
    def __len__(self):
        return len(self.fields)
    
    def __iter__(self):
        i = 0
        for bfield in self.form:
            i += 1
            bf = BoundField(bfield,self)
            bf.position = i
            yield bf
            
    def is_valid(self):
        '''
        Check if form is valid.
        If not fill the ajax errors dictionary
        '''
        f = self.form
        if not f:
            return True
        valid = f.is_valid()
        self.jerrors = jerrors()
        err   = self.jerrors
        if not valid:
            for fname, error in f.errors.iteritems():
                field  = f[fname]
                bf     = BoundField(field,f)
                # make sure force_unicode is applied to the error elements!!!
                errli  = '%s' % ''.join(['<p>%s</p>' % force_unicode(e) for e in error])
                err.add('#%s' % bf.errorid(), errli)
        return valid
    
    def __get_cleaned_data(self):
        try:
            return self.form.cleaned_data
        except:
            return {}
    cleaned_data = property(fget = __get_cleaned_data)
    
    def save(self, *args):
        if self.form:
            return self.form.save(*args)
        else:
            return None
        

    
class quickform(form):
    '''
    Shortcut for a simple form
    '''
    def __init__(self, form = None,
                 submitname = None,
                 submitvalue = 'Submit',
                 layout = 'twocolumns',
                 *args, **kwargs):
        self.formtype    = form
        self.submitname  = submitname
        self.submitvalue = submitvalue
        self.layout      = layout
        super(quickform,self).__init__(*args, **kwargs)
        
    def _make(self, data = None, object = None, initial = None, prefix = None, *args, **kwargs):
        f = self.formtype
        if isforminstance(f):
            ft = f.__class__
        else:
            ft = f
        if ft:
            name = self.submitname or str(ft.__name__)
        else:
            name = self.submitname or slugify(self.submitvalue)
        name = name.lower()
        co   = self.make_container()
        co['form'] = formlet(form     = self.formtype,
                             data     = data,
                             initial  = initial,
                             object   = object,
                             view     = self.view,
                             layout   = self.layout,
                             request  = self.request,
                             template = self.template,
                             prefix   = prefix,
                             submit   = submit(name = name, value = self.submitvalue)).addclass(name)
    
            
    
    
def formmodel(formlet):
    
    def __init__(self, model, **attrs):
        self.model = model
        super(formmodel, self).__init__(**attrs)
        
    
    