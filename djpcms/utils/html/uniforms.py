#
# Uniform for django.
# Adapted from http://github.com/pydanny/django-uni-form
#
#
"""
Utilities for helping developers use python for adding various attributes,
elements, and UI elements to forms generated via the uni_form template tag.

"""
from django.template import loader 
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms.forms import BoundField
from django.utils.safestring import mark_safe

from djpcms.utils.ajax import jhtmls

__all__ = ['FormHelper','FormLayout','Fieldset','Row','HtmlForm']

#_required_tag = mark_safe('<em>*</em>')
_required_tag = mark_safe('')

#default renderer for forms
def_renderer = lambda x: x


def render_field(field, form):
    if isinstance(field, str):
        return render_form_field(form, field)
    else:
        return field.render(form)
    
def get_rendered_fields(form):
    rf = getattr(form, 'rendered_fields', [])
    form.rendered_fields = rf
    return rf


def render_form_field(form, field):
    try:
        field_instance = form.fields[field]
    except KeyError:
        raise Exception("Could not resolve form field '%s'." % field)
    bound_field = BoundField(form, field_instance, field)
    html = loader.render_to_string("djpcms/uniform/field.html", {'field': bound_field, 'required': _required_tag})
    rendered_fields = get_rendered_fields(form)
    if not field in rendered_fields:
        rendered_fields.append(field)
    else:
        raise Exception("A field should only be rendered once: %s" % field)
    return html


class FormLayout(object):
    '''
Form Layout, add fieldsets, rows, fields and html

example:

>>> layout = Layout(Fieldset('', 'is_company'),
... Fieldset(_('Contact details'),
... 'email',
... Row('password1','password2'),
... 'first_name',
... 'last_name',
... HTML('<img src="/media/somepicture.jpg"/>'),
... 'company'))
>>> helper.add_layout(layout)
'''
    def __init__(self, *fields, **kwargs):
        self.template = kwargs.get('template',None)
        self._allfields = []
        self.add(*fields)
    
    def add(self,*fields):
        for field in fields:
            self._allfields.append(field)
            if field.key:
                setattr(self,field.key,field)

    def render(self, helperOrform):
        '''Render the uniform layout'''
        form = helperOrform
        ishelper = False
        if isinstance(helperOrform,FormHelper):
            form = helperOrform.form
            ishelper = True
        ctx  = {}
        html = ''
        for field in self._allfields:
            if field.key and self.template:
                ctx[field.key] = render_field(field, form)
            else:
                html += render_field(field, form)
        
        rendered_fields = get_rendered_fields(form)
        for field in form.fields.keys():
            if not field in rendered_fields:
                html += render_field(field, form)
                
        if ctx:
            ctx['html'] = mark_safe(html)
            if ishelper:
                ctx['inputs'] = helperOrform.render_inputs()
                ctx['inlines'] = helperOrform.render_inlines()
            return loader.render_to_string(self.template, ctx)
        else:
            if ishelper:
                html += helperOrform.render_inlines()
                html += helperOrform.render_inputs()
            return mark_safe(html)


class FormElement(object):
    
    def __new__(cls, *args, **kwargs):
        obj = super(FormElement,cls).__new__(cls)
        obj.renderer = kwargs.pop('renderer',def_renderer)
        obj.key = kwargs.pop('key',None)
        return obj

    def render(self, form):
        return self.renderer(self._render(form))
    
    def _render(self, form):
        raise NotImplementedError

class Fieldset(FormElement):
    ''' Fieldset container. Renders to a <fieldset>. '''
    
    inlineLabels = 'inlineLabels'
    blockLabels  = 'blockLabels'
    
    def __init__(self, *fields, **kwargs):
        self.css = kwargs.get('css_class','blockLabels2')
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


class Row(FormElement):
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

class Column(FormElement):
    ''' column container. Renders to a set of <div>'''
    def __init__(self, *fields, **kwargs):
        self.fields = fields
        if 'css_class' in kwargs.keys():
            self.css = kwargs['css_class']
        else:
            self.css = "formColumn"

    def _render(self, form):
        output = u'<div class="%s">' % self.css
        for field in self.fields:
            output += render_field(field, form)
        output += u'</div>'
        return u''.join(output)

class HtmlForm(FormElement):

    ''' HTML container '''

    def __init__(self, html, **kwargs):
        self.html = html

    def _render(self, form):
        return self.html
    

class FormInline(object):
    '''Inline form'''
    def __init__(self, model = None):
        self.model = model


class FormHelper(object):

    def __init__(self, enctype = 'multipart/form-data'):
        self.attr = {}
        self.attr['method']  = 'post'
        self.attr['action']  = ''
        self.attr['enctype'] = enctype
        self.attr['id']      = ''
        self.attr['class']   = 'uniForm'
        self.inputs  = []
        self.layout  = FormLayout()
        self.tag     = True
        self.use_csrf_protection = False
        self.ajax    = None
        self.inlines = []
        self.form    = None

    def add_input(self, input_object):
        self.inputs.append(input_object)

    def render_layout(self):
        return mark_safe(self.layout.render(self))
    
    def render_inputs(self):
        if self.inputs:
            return loader.render_to_string('djpcms/uniform/inputs.html',
                                           {'inputs': self.inputs})
        else:
            return ''
    
    def render_inlines(self):
        if self.inlines:
            return loader.render_to_string('djpcms/uniform/inlines.html',
                                           {'inlines': self.inlines})
        else:
            return ''
            

    def flatattr(self):
        attr = []
        for k,v in self.attr.items():
            if v:
                attr.append('%s="%s"' % (k,v))
        if attr:
            return mark_safe(' %s' % ' '.join(attr))
        else:
            return ''
    
    def render(self, form):
        self.form = form
        return loader.render_to_string('djpcms/uniform/uniform.html',
                                       {'helper': self})

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
    
    def json_errors(self, form):
        '''
        Serialize form errors for AJAX-JSON interaction
        '''
        jerr = jhtmls()
        for name,errs in form.errors.items():
            field_instance = form.fields.get(name,None)
            if field_instance:
                bound_field = BoundField(form, field_instance, name)
                jerr.add('#%s-errors' % bound_field.auto_id,str(errs),alldocument = False)
        return jerr
    
    def json_form_error(self, form, e):
        return jhtmls(identifier = '.form-messages',
                      html = '<div class="errorlist">%s</div>' % e,
                      alldocument = False)
        
        