#
# Uniform for django.
# Adapted from http://github.com/pydanny/django-uni-form
#
#
from django.template import loader 
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms.forms import BoundField
from django.forms.formsets import all_valid
from django.utils.safestring import mark_safe
# Wild import af all django forms stuff
from django.forms import *

from djpcms.utils.ajax import jhtmls
from djpcms.utils.uniforms.uniformset import ModelFormInlineHelper


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
    '''Form Layout, add fieldsets, rows, fields and html.
Valid key-value arguments are (all optionals):
* *template*: a template file name.

example:

>>> layout = Layout(
... Fieldset('', 'is_company'),
... Fieldset('email',
... Row('password1','password2'),
... 'first_name',
... 'last_name',
... HTML('<img src="/media/somepicture.jpg"/>'),
... 'company'))
>>> helper.layout = layout
'''
    def __init__(self, *fields, **kwargs):
        self.template = kwargs.get('template',None)
        self.default_style = kwargs.get('template',None)
        self._allfields = []
        self.add(*fields)
    
    def add(self,*fields):
        '''Add *fields* to all fields. A field must be an instance of :class:`UniFormElement`.'''
        for field in fields:
            if isinstance(field,UniFormElement):
                self._allfields.append(field)
                if field.key:
                    setattr(self,field.key,field)

    def render(self, form, formsets = None, inputs = None):
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
            ctx['inputs'] = inputs
            ctx['inlines'] = formsets
            return loader.render_to_string(self.template, ctx)
        else:
            if formsets:
                html += formsets
            if inputs:
                html += inputs
            return mark_safe(html)


class UniFormElement(object):
    '''Base class of elements in a uni-form :class:`FormLayout`'''
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


class HtmlForm(UniFormElement):

    ''' HTML container '''

    def __init__(self, html, **kwargs):
        self.html = html

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
    

class FormHelper(UniFormBase):
    '''Main uniform class used to inject layout and other properties to raw forms.
For example::

    from django import forms
    from djpcms.utils import uniforms

    class StrategyForm(forms.Form):
        name = forms.CharField()
        description = forms.TextField()
        
        helper = uniforms.FormHelper()
    
example with inline formlets::

    class StrategyForm(forms.ModelForm):
        helper = FormHelper()
        helper.inlines.append(LegForm)
        
            
.. attribute:: default_style
 
    The default style to apply to layout.
    
.. attribute:: layout
 
    Instance of :class:`FormLayout`.
    
.. attribute:: ajax
 
    A string indicating the ``AJAX`` class or ``None``.
'''
    def __init__(self, enctype = 'multipart/form-data',
                 layout = None, method = 'post',
                 default_style = None):
        self.attr = {}
        self.attr['method']  = method
        self.attr['action']  = ''
        self.attr['enctype'] = enctype
        self.attr['id']      = ''
        self.attr['class']   = 'uniForm'
        self.inputs  = []
        self.default_style   = default_style or inlineLabels
        self.__layout        = None
        self.layout          = layout or FormLayout()
        self.use_csrf_protection = False
        self.ajax            = None
        self.inlines         = []
        
    def __get_layout(self):
        return self.__layout
    def __set_layout(self, layout):
        if isinstance(layout,FormLayout):
            layout.default_style = self.default_style
            self.__layout = layout
    layout = property(__get_layout,__set_layout)

    def add_input(self, input_object):
        self.inputs.append(input_object)
    
    def json_errors(self, form):
        '''Serialize form errors for AJAX-JSON interaction.
        '''
        jerr = jhtmls()
        form = form.form
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
        

class UniForm(UniFormBase):
    '''Class holding a form, formsets and helper for displaying forms as uni-forms.'''
    def __init__(self,
                 form,
                 request = None,
                 instance = None,
                 action = '.',
                 inputs = None,
                 tag = True):
        helper = getattr(form,'helper',None)
        if not helper:
            helper = FormHelper()
            form.helper = helper
        self.attr     = helper.attr.copy()
        self.helper   = helper
        self.attr['action'] = action
        self.form     = form
        self.inputs   = inputs or []
        self.tag      = tag
        self.formsets = self._build_fsets(request,instance)
        
    def __get_media(self):
        return self.form.media
    media = property(__get_media)
        
    def is_valid(self):
        if self.form.is_valid():
            return all_valid(self.formsets)
        else:
            return False

    def render(self):
        return loader.render_to_string('djpcms/uniforms/uniform.html',
                                       {'uniform': self,
                                        'form': self.render_layout()})
        
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
        
    def render_layout(self):
        return mark_safe(self.helper.layout.render(self.form,
                                                   self.render_inlines(),
                                                   self.render_inputs()))
    
    def _build_fsets(self, request, instance):
        formsets = []
        prefixes = {}
        for inline in self.helper.inlines:
            prefix  = inline.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = inline.get_formset(request = request,
                                         instance = instance,
                                         prefix   = prefix)
            formsets.append(formset)
        return formsets
    