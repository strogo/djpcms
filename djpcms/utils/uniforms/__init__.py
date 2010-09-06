#
# Uniform for django.
# Adapted from http://github.com/pydanny/django-uni-form
#
#
from django.forms.formsets import all_valid
# Wild import af all django forms stuff
from django.forms import *

from djpcms.contrib import messages
from djpcms.template import loader
from djpcms.utils import mark_safe
from djpcms.utils.ajax import jhtmls
from djpcms.utils.uniforms.uniformset import BoundField, ModelFormInlineHelper


inlineLabels   = 'inlineLabels'
blockLabels    = 'blockLabels'
blockLabels2   = 'blockLabels2'
inlineFormsets = 'blockLabels2'


#_required_tag = mark_safe('<em>*</em>')
_required_tag = mark_safe('')

#default renderer for forms
def_renderer = lambda x: x


def render_field(field, form):
    if isinstance(field, str):
        return render_form_field(field, form)
    else:
        return field.render(form)
    
def get_rendered_fields(form):
    rf = getattr(form, 'rendered_fields', [])
    form.rendered_fields = rf
    return rf


def render_form_field(field, form):
    try:
        field_instance = form.fields[field]
    except KeyError:
        raise Exception("Could not resolve form field '%s'." % field)
    bound_field = BoundField(form, field_instance, field)
    html = loader.render_to_string("djpcms/uniforms/field.html",
                                   {'field': bound_field,
                                    'required': _required_tag})
    rendered_fields = get_rendered_fields(form)
    if not field in rendered_fields:
        rendered_fields.append(field)
    else:
        raise Exception("A field should only be rendered once: %s" % field)
    return html


class FormLayout(object):
    '''Form Layout, add fieldsets, rows, columns and html.
Valid key-value arguments are (all optionals):

* *id*: string id for layout.
* *template*: a template file name.
* *default_style*: the default layout style used for fields left out.

Example::

    class NoteForm(forms.Form):
        name = forms.CharField()
        dt   = forms.DateTimeField()
        content = forms.TextField()
    
        layout = FormLayout(Fieldset('name', 'dt'),
        Fieldset('description'),
        Row('password1','password2'),
        HtmlForm('<img src="/media/somepicture.jpg"/>'))


'''
    def __init__(self, *fields, **kwargs):
        self.id = kwargs.get('id',None)
        self.template = kwargs.get('template',None)
        self.default_style = kwargs.get('default_style',inlineLabels)
        self._allfields = []
        self.inlines    = []
        self.add(*fields)
    
    def add(self,*fields):
        '''Add *fields* to all fields. A field must be an instance of :class:`UniFormElement`.'''
        for field in fields:
            if isinstance(field,UniFormElement):
                self._allfields.append(field)
                if field.key:
                    setattr(self,field.key,field)

    def render(self, form):
        '''Render the uniform layout:
* *form* a form instance.
* *formsets* a string which render inline formsets.
* *inputs* safe string which render the submit inputs.'''
        ctx  = {}
        html = ''
        for field in self._allfields:
            if field.key and self.template:
                ctx[field.key] = render_field(field, form)
            else:
                html += render_field(field, form)
        
        missing_fields = []
        rendered_fields = get_rendered_fields(form)
        for field in form.fields.keys():
            if not field in rendered_fields:
                missing_fields.append(field)
        
        if missing_fields:
            fset = Fieldset(*missing_fields,**{'css_class':self.default_style})        
            html += fset.render(form)
                
        if ctx:
            ctx['html'] = mark_safe(html)
            html = loader.render_to_string(self.template, ctx)
        else:
            html = mark_safe(html)
        
        if self.id:
            return mark_safe('<div id="%s">%s</div>' % (self.id,html))
        else:
            return html


class UniFormElement(object):
    '''Base class of elements in a uni-form :class:`FormLayout`'''
    __metaclass__ = MediaDefiningClass
    
    def __new__(cls, *args, **kwargs):
        obj = super(UniFormElement,cls).__new__(cls)
        obj.renderer = kwargs.pop('renderer',def_renderer)
        obj.key = kwargs.pop('key',None)
        return obj

    def render(self, form):
        return self.renderer(self._render(form))
    
    def _render(self, form):
        raise NotImplementedError


class Fieldset(UniFormElement):
    ''' Fieldset container. Renders to a <fieldset>. '''
    
    def __init__(self, *fields, **kwargs):
        self.css = kwargs.get('css_class',blockLabels2)
        self.legend_html = kwargs.get('legend','')
        if self.legend_html:
            self.legend_html = '<legend>%s</legend>' % unicode(self.legend_html)
        self.fields = fields

    def _render(self, form):
        if self.css:
            html = u'<fieldset class="%s">' % self.css
        else:
            html = u'<fieldset>'
        html += self.legend_html
        for field in self.fields:
            html += render_field(field, form)
        html += u'</fieldset>'
        return mark_safe(html)


class Row(UniFormElement):
    ''' row container. Renders to a set of <div>'''
    def __init__(self, *fields, **kwargs):
        self.fields = fields
        if 'css_class' in kwargs.keys():
            self.css = kwargs['css_class']
        else:
            self.css = "formRow"

    def _render(self, form):
        output = u'<div class="%s">' % self.css
        for field in self.fields:
            output += render_field(field, form)
        output += u'</div>'
        return u''.join(output)


class Column(UniFormElement):
    ''' column container. Renders to a set of <div>'''
    def __init__(self, *fields, **kwargs):
        self.fields = fields
        ncols = kwargs.get('num_cols',None)
        if 'css_class' in kwargs.keys():
            self.css = kwargs['css_class']
        else:
            self.css = "formColumn blockLabels2"
        if ncols:
            self.css += " cols%s" % ncols

    def _render(self, form):
        output = u'<div class="%s">' % self.css
        for field in self.fields:
            output += render_field(field, form)
        output += u'</div>'
        return u''.join(output)


class Html(UniFormElement):

    ''' HTML container '''

    def __init__(self, html, **kwargs):
        self.html = mark_safe(html)

    def _render(self, form):
        return self.html
    
    
class UniFormBase(object):
    
    def flatattr(self):
        attr = []
        for k,v in self.attr.items():
            if v:
                attr.append('%s="%s"' % (k,v))
        if attr:
            return mark_safe(' %s' % ' '.join(attr))
        else:
            return ''
        
    def addClass(self, cn):
        if cn:
            cn = str(cn).replace(' ','')
        if cn:
            attrs = self.attr
            c    = attrs.get('class',None)
            if c:
                cs = c.split(' ')
                if cn not in cs:
                    attrs['class'] = '%s %s' % (c,cn)
            else:
                attrs['class'] = cn
        return self
    
      
class UniForm(UniFormBase):
    '''Class holding a form, formsets and helper for displaying forms as uni-forms.'''
    default_template = 'djpcms/uniforms/uniform.html'
    default_error_msg = 'There were errors. Try again.' 
    
    def __init__(self,
                 form,
                 template = None,
                 request = None,
                 instance = None,
                 method = 'post',
                 enctype = 'multipart/form-data',
                 error_message = None,
                 action = '.',
                 inputs = None,
                 tag = True,
                 csfr = True):
        self.use_csrf_protection = csfr
        self.attr = {}
        self.attr['method']  = method
        self.attr['action']  = ''
        self.attr['enctype'] = enctype
        self.attr['id']      = ''
        self.attr['class']   = 'uniForm'
        self.attr['action']  = action
        self.forms           = []
        self.formsets        = []
        self.inputs          = inputs or []
        self.tag             = tag
        self._messages       = []
        self._errors         = []
        self.is_ajax         = False
        self.error_message   = error_message if error_message is not None else self.default_error_msg
        self.template        = template or self.default_template
        self.add(form,request,instance)
    
    def add(self, form, request = None, instance = None):
        if not form:
            return False
        elif isinstance(form,BaseForm):
            form.layout = getattr(form,'layout',None) or FormLayout()
            self._build_fsets(form,request,instance)
            self.forms.append((form.layout,form))
        else:
            form = Html(form)
            self.forms.append((form,form))
        return True
    
    def __getitem__(self, index):
        return self.forms[index][1]
    
    def __get_media(self):
        media = None
        for form in self.forms:
            fmedia = form[1].media
            media = fmedia if media is None else media + fmedia
        return media
    media = property(__get_media)
        
    def is_valid(self):
        for form in self.forms:
            form = form[1]
            if isinstance(form,BaseForm):
                if not form.is_valid():
                    return False
        return all_valid(self.formsets)
    
    def save(self, commit = True):
        instance = None
        for form in self.forms:
            save = getattr(form[1],'save',None)
            if save:
                instance = save(commit = commit)
        return instance
    
    def add_message(self, request, msg, error = False):
        msg = str(msg)
        if error:
            self._errors.append(msg)
            if not self.is_ajax:
                messages.error(request,msg)
        else:
            self._messages.append(msg)
            if not self.is_ajax:
                messages.info(request,msg)
            
    def json_message(self):
        msg = self._make_messages('messagelist',self._messages)
        err = self._make_messages('errorlist',self._errors)
        return jhtmls(identifier = '.form-messages', html = msg+err, alldocument = False)
    
    def json_errors(self, withmessage = True):
        '''Serialize form errors for AJAX-JSON interaction.
        '''
        jerr = jhtmls()
        for form in self.forms:
            form = form[1]
            if isinstance(form,BaseForm):
                for name,errs in form.errors.items():
                    field_instance = form.fields.get(name,None)
                    if field_instance:
                        bound_field = BoundField(form, field_instance, name)
                        jerr.add('#%s-errors' % bound_field.auto_id,str(errs),alldocument = False)
        for formset in self.formsets:
            form = formset.form
            for name,errs in form.errors.items():
                pass
        #if jerr and self.error_message and withmessage:
        #    self.add_message(self.error_message,error=True)
        jerr.update(self.json_message())
        return jerr
    
    @property
    def cleaned_data(self):
        cd = {}
        for form in self.forms:
            cd.update(form[1].cleaned_data)
        return cd

    def render(self):
        fdict = {}
        forms = []
        num = 0
        for layout,form in self.forms:
            num += 1
            html = layout.render(form)
            forms.append(html)
            fdict['html%s' % num] = html
        return loader.render_to_string(self.template,
                                       {'uniform': self,
                                        'forms': forms,
                                        'fdict': fdict,
                                        'inputs': self.render_inputs(),
                                        'inlines': self.render_inlines()})
        
    def render_inputs(self):
        if self.inputs:
            return loader.render_to_string('djpcms/uniforms/inputs.html',
                                           {'inputs': self.inputs})
        else:
            return ''
    
    def render_inlines(self):
        if self.formsets:
            return loader.render_to_string('djpcms/uniforms/inlines.html',
                                           {'form_inlines': self.formsets,
                                            'field_class': inlineFormsets})
        else:
            return ''
    
    def _build_fsets(self, form, request, instance):
        formsets = self.formsets
        prefixes = {}
        for inline in form.layout.inlines:
            prefix  = inline.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = inline.get_formset(request = request,
                                         instance = instance,
                                         prefix   = prefix)
            formsets.append(formset)
    
    def _make_messages(self, cname, mlist):
        if mlist:
            return '<ul class="%s"><li>%s</li></ul>' % (cname,'</li><li>'.join(mlist))
        else:
            return ''
            