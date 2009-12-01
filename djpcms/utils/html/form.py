#
#    Utility for managing django forms
#
from django.utils.encoding import force_unicode
from django import forms

from djpcms.utils.ajax import jhtmls, jerrors, jredirect
from djpcms.utils.func import slugify, isforminstance

from base import htmlattr, htmltiny, htmlcomp
from boundfield import BoundField


__all__ = ['form','formlet','submit']

FORMLET_TEMPLATES      = {'onecolumn':    ['form/onecolumn.html',
                                           'djpcms/form/onecolumn.html'],
                          'twocolumns':   ['form/twocolumns.html',
                                           'djpcms/form/twocolumns.html'],
                          'threecolumns': ['form/threecolumns.html',
                                           'djpcms/form/threecolumns.html'],
                          'flat-notag':   ['form/flat_notag.html',
                                           'djpcms/form/flat_notag.html'],
                          'flat':         ['form/flat.html',
                                           'djpcms/form/flat.html']}


class submit(htmltiny):
    
    def __init__(self, name = 'submit', value = 'submit', **attrs):
        super(submit,self).__init__('input', name = name, value = value, **attrs)
        self._attrs['type'] = 'submit'


class form(htmlcomp):
    
    def __init__(self, method = 'post', url = None, **attrs):
        super(form,self).__init__('form', **attrs)
        self.url = url or '.'
        self._attrs['method'] = method
        self._attrs['action'] = self.url
        self.jerrors   = None
    
    def messagepost(self, html):
        return jhtmls(html = html, identifier = '.%s' % self.ajax.formmessages)
    
    def errorpost(self, html):
        '''
        a form error message
        '''
        ehtml = u'\n'.join(['<div class="%s">' % self.ajax.errorlist,
                            html,
                            '</div>'])
        return self.messagepost(ehtml)
    
    def redirect(self, url):
        return jredirect(url)
    
    def __get_instance(self):
        '''
        It assume only one model instance can exist
        '''
        flets = self.getplugins(formlet)
        id = None
        for flet in flets:
            id_ = flet.instance                
            if id_:
                id = id_
        return id
    instance = property(__get_instance)
    
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
    
    def save(self, commit = True):
        flets = self.getplugins(formlet)
        id = None
        for flet in flets:
            id_ = flet.save(commit = commit)
            if id_:
                id = id_
        return id    
        

class formlet(htmlattr):
    '''
    Simple wrapper for a django Form
    '''
    def __init__(self,
                 form = None,
                 template = None,
                 layout = None,
                 submit = None, **attrs):
        '''
        Initialize the formlet.
            layout:    The layout when rendering the form
                        onecolumn:   render as 1 column table
                        twocolumns:  render as a 2 columns table (default)
                        flat:        render as one row
                        custom:      custom template
        '''
        super(formlet,self).__init__(**attrs)
        if template is None:
            layout   = layout or 'twocolumns'
            template = FORMLET_TEMPLATES.get(layout,None)
        if not template:
            template = FORMLET_TEMPLATES.get('twocolumns',None)
        self.template = template
        self.form     = form
        self.jerrors  = None
        
        if submit:
            if not isinstance(submit,list):
                submit = [submit]
            self.submits = submit
        else:
            self.submits  = []
            
    def __getattr__(self, fname):
        form = self.form
        if form:
            try:
                bf = form[fname]
            except:
                return None
            return BoundField(bf,self)
        else:
            return None
                
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
    
    def save(self, commit = True):
        if isinstance(self.form,forms.ModelForm):
            return self.form.save(commit = commit)
        else:
            return None
        
    def __get_instance(self):
        '''
        It assume only one model instance can exist
        '''
        try:
            return self.form.instance
        except:
            return None
    instance = property(__get_instance)
        

    
        
    
