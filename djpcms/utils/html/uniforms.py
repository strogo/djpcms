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


__all__ = ['FormHelper','FormLayout','Fieldset','Row','HtmlForm']



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
    html = loader.render_to_string("djpcms/uniform/field.html", {'field': bound_field})
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
        self._allfields = fields
        self.fields = []
        for field in fields:
            if field.key:
                setattr(self,field.key,field)
            else:
                self.fields.append(field)
        self.template = kwargs.get('template',None)

    def render(self, helper):
        form = helper.form
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
            ctx['inputs'] = helper.render_inputs()
            return loader.render_to_string(self.template, ctx)
        else:
            html += helper.render_inputs()
            return mark_safe(html)

def_renderer = lambda x: x

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




class FormHelper(object):
    """
By setting attributes to me you can easily create the text that goes
into the uni_form template tag. One use case is to add to your form
class.

Special attribute behavior:

method: Defaults to POST but you can also do 'GET'

form_action: applied to the form action attribute. Can be a named url in
your urlconf that can be executed via the *url* default template tag or can
simply point to another URL.

id: Generates a form id for dom identification.
If no id provided then no id attribute is created on the form.

class: add space seperated classes to the class list.
Defaults to uniForm.
Always starts with uniForm even do specify classes.

form_tag: Defaults to True. If set to False it renders the form without the form tags.

use_csrf_protection: Defaults to False. If set to True a CSRF protection token is
rendered in the form. This should only be left as False for forms targeting
external sites or internal sites without CSRF protection (as described in the
Django documentation).
Requires the presence of a csrf token in the current context with the identifier
"csrf_token" (which is automatically added to your context when using RequestContext).


Demonstration:

First we create a MyForm class and instantiate it

>>> from django import forms
>>> from uni_form.helpers import FormHelper, Submit, Reset
>>> from django.utils.translation import ugettext_lazy as _
>>> class MyForm(forms.Form):
... title = forms.CharField(label=_("Title"), max_length=30, widget=forms.TextInput())
... # this displays how to attach a formHelper to your forms class.
... helper = FormHelper()
... helper.form_id = 'this-form-rocks'
... helper.form_class = 'search'
... submit = Submit('search','search this site')
... helper.add_input(submit)
... reset = Reset('reset','reset button')
... helper.add_input(reset)

After this in the template::

{% load uni_form_tags %}
{% uni_form form form.helper %}


"""

    def __init__(self, enctype = 'multipart/form-data'):
        self.attr = {}
        self.attr['method']  = 'post'
        self.attr['action']  = ''
        self.attr['enctype'] = enctype
        self.attr['id']      = ''
        self.attr['class']   = 'uniForm'
        self.inputs = []
        self.layout = None
        self.tag    = True
        self.use_csrf_protection = False
        self.form   = None

    def add_input(self, input_object):
        self.inputs.append(input_object)

    def add_layout(self, layout):
        self.layout = layout

    def render_layout(self):
        layout = self.layout
        if not layout:
            layout = FormLayout()
        return mark_safe(layout.render(self))
    
    def render_inputs(self):
        if self.inputs:
            return loader.render_to_string('djpcms/uniform/inputs.html',
                                           {'inputs': self.inputs})
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