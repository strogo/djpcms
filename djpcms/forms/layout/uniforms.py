from djpcms.contrib import messages
from djpcms.template import loader
from djpcms.utils.ajax import jhtmls

from .base import FormLayout, BaseMedia


inlineLabels   = 'inlineLabels'
inlineLabels2  = 'inlineLabels fullwidth'
inlineLabels3  = 'inlineLabels auto'
blockLabels    = 'blockLabels'
blockLabels2   = 'blockLabels2'
inlineFormsets = 'blockLabels2'
nolabel        = 'nolabel'
default_style  = 'inlineLabels'


def default_csrf():
    return 'django.middleware.csrf.CsrfViewMiddleware' in sites.settings.MIDDLEWARE_CLASSES

#_required_tag = mark_safe('<em>*</em>')
_required_tag = lambda : loader.mark_safe('')

#default renderer for forms
def_renderer = lambda x: x


def render_field(field, form, layout, css_class):
    if isinstance(field, str):
        return render_form_field(field, form, layout, css_class)
    else:
        return field.render(form, layout)
    
def get_rendered_fields(form):
    rf = getattr(form, 'rendered_fields', [])
    form.rendered_fields = rf
    return rf


def render_form_field(field, form, layout, css_class):
    try:
        field_instance = form.fields[field]
    except KeyError:
        raise Exception("Could not resolve form field '%s'." % field)
    bound_field = BoundField(form, field_instance, field)
    label = None if css_class == nolabel else bound_field.label 
    html = loader.render_to_string("djpcms/uniforms/field.html",
                                   {'field': bound_field,
                                    'label': label,
                                    'required': _required_tag()})
    rendered_fields = get_rendered_fields(form)
    if not field in rendered_fields:
        rendered_fields.append(field)
    else:
        raise Exception("A field should only be rendered once: %s" % field)
    return html


class UniFormElement(object):
    '''Base class for elements in a uniform :class:`FormLayout`.
    
    .. attribute:: css_class
    
        The class used for the form element, one of :ref:`layout types <uniforms-layouts>`.
        If missing the :attr:`FormLayout.default_style` will be used.
        
    .. attribute:: elem_css
    
        Extra css class for the element. Default ``None``.
        
    .. attribute:: template
    
        An optional template file name for rendering the element. Default ``None``.
    '''
    elem_css = None
    
    def __new__(cls, *args, **kwargs):
        obj = super(UniFormElement,cls).__new__(cls)
        obj.renderer = kwargs.pop('renderer',def_renderer)
        obj.key = kwargs.pop('key',None)
        obj.css = kwargs.get('css_class',None)
        obj.template = kwargs.get('template',None)
        obj.elem_css = kwargs.get('elem_css',cls.elem_css)
        return obj
    
    def _css(self, layout):
        dcss = None if layout is None else layout.default_style
        css = self.css or dcss
        if self.elem_css:
            css = '%s %s' % (css,self.elem_css)
        return css

    def render(self, form, layout = None):
        '''Render the uniform element. This function is called the the instance of
:class:`FormLayout` which contains ``self``.'''
        return self.renderer(self._render(form, layout))
    
    def _render(self, form, layout):
        raise NotImplementedError


class Fieldset(UniFormElement):
    '''A :class:`UniFormElement` which renders to a <fieldset>.'''
    
    def __init__(self, *fields, **kwargs):
        self.legend_html = kwargs.get('legend','')
        if self.legend_html:
            self.legend_html = '<legend>%s</legend>' % unicode(self.legend_html)
        self.fields = fields

    def _render(self, form, layout):
        if self.css:
            html = u'<fieldset class="%s">' % self.css
        else:
            html = u'<fieldset>'
        html += self.legend_html
        for field in self.fields:
            html += render_field(field, form, layout, self.css)
        html += u'</fieldset>'
        return loader.mark_safe(html)


class Row(UniFormElement):
    '''A :class:`UniFormElement` which renders to a <div>.'''
    elem_css = "formRow"
    def __init__(self, *fields, **kwargs):
        self.legend_html = kwargs.get('legend','')
        if self.legend_html:
            self.legend_html = '<legend>%s</legend>' % unicode(self.legend_html)
        self.fields = fields

    def _render(self, form, layout):
        css = self._css(layout)
        output = u'%s<div class="%s">' % (self.legend_html,css)
        for field in self.fields:
            output += render_field(field, form, layout, self.css)
        output += u'</div>'
        return u''.join(output)


class Columns(UniFormElement):
    '''A :class:`UniFormElement` whiche defines a set of columns. Renders to a set of <div>.'''
    elem_css  = "formColumn"
    templates = {2: 'djpcms/yui/yui-simple.html',
                 3: 'djpcms/yui/yui-simple3.html'}
    def __init__(self, *columns, **kwargs):
        self.columns = columns
        ncols = len(columns)
        if not self.template:
            self.template = self.templates.get(ncols,None)
        if not self.template:
            raise ValueError('Template not available in uniform Column.')

    def _render(self, form, layout):
        css = self._css(layout)
        content = {}
        for i,column in enumerate(self.columns):
            output = u'<div class="%s">' % css
            for field in column:
                output += render_field(field, form, layout, self.css)
            output += u'</div>'
            content['content%s' % i] = loader.mark_safe(output)
        return loader.render_to_string(self.template, content)


class Html(UniFormElement):
    '''A :class:`UniFormElement` which renders to `self`.'''
    def __init__(self, html, **kwargs):
        self.html = mark_safe(html)

    def _render(self, form, layout):
        return self.html
    


class Layout(FormLayout):
    '''Main class for defining the layout of a uniform.
'''
    def __init__(self, *fields, **kwargs):
        self.template = kwargs.get('template',None)
        self.default_style = kwargs.get('default_style',default_style)
        self._allfields = []
        self.inlines    = []
        self.add(*fields)
        
    def add(self,*fields):
        '''Add *fields* to all fields. A field must be an instance of :class:`UniFormElement`.'''
        for field in fields:
            if isinstance(field,UniFormElement):
                if not field.css:
                    field.css = self.default_style
                self._allfields.append(field)
                if field.key:
                    setattr(self,field.key,field)

    def render(self, form, inputs = None):
        '''Render the uniform layout or *form*.'''
        ctx  = {}
        html = ''
        for field in self._allfields:
            h = field.render(form, self)
            if field.key and self.template:
                ctx[field.key] = h
            else:
                html += h
        
        missing_fields = []
        rendered_fields = get_rendered_fields(form)
        for field in form.fields.keys():
            if not field in rendered_fields:
                missing_fields.append(field)
        
        if missing_fields:
            fset = Fieldset(*missing_fields,**{'css_class':self.default_style})        
            html += fset.render(form,self)
                
        if ctx:
            ctx['inputs'] = inputs
            ctx['html'] = loader.mark_safe(html)
            html = loader.render_to_string(self.template, ctx)
        else:
            html = loader.mark_safe(html)
        
        if self.id:
            return loader.mark_safe('<div id="%s">%s</div>' % (self.id,html))
        else:
            return html
    
      