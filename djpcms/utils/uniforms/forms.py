#
# Uniform for django.
# Adapted from http://github.com/pydanny/django-uni-form
#
#
from django.forms.formsets import all_valid

from djpcms import sites
from djpcms.forms import BoundField, fill_form_data, MediaDefiningClass, BaseForm
from djpcms.contrib import messages
from djpcms.template import loader, RequestContext, mark_safe
from djpcms.utils.ajax import jhtmls


__all__ = ['inlineLabels',
           'inlineLabels2',
           'inlineLabels3',
           'blockLabels',
           'blockLabels2',
           'inlineFormsets',
           'nolabel',
           'default_style',
           'FormLayout',
           'UniFormElement',
           'Fieldset',
           'Row',
           'Columns',
           'Html',
           'UniForm']


inlineLabels   = 'inlineLabels'
inlineLabels2  = 'inlineLabels fullwidth'
inlineLabels3  = 'inlineLabels auto'
blockLabels    = 'blockLabels'
blockLabels2   = 'blockLabels2'
inlineFormsets = 'blockLabels2'
nolabel        = 'nolabel'
default_style  = inlineLabels

def default_csrf():
    return 'django.middleware.csrf.CsrfViewMiddleware' in sites.settings.MIDDLEWARE_CLASSES

#_required_tag = mark_safe('<em>*</em>')
_required_tag = mark_safe('')

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
                                    'required': _required_tag})
    rendered_fields = get_rendered_fields(form)
    if not field in rendered_fields:
        rendered_fields.append(field)
    else:
        raise Exception("A field should only be rendered once: %s" % field)
    return html


class FormLayout(object):
    '''Main class for defining the layout of a uniform. For example::

    class NoteForm(forms.Form):
        name = forms.CharField()
        dt   = forms.DateTimeField()
        content = forms.TextField()
    
        layout = FormLayout(Fieldset('name', 'dt'),
                            Fieldset('description'),
                            Row('password1','password2'),
                            Html('<img src="/media/somepicture.jpg"/>'))
                            
    
.. attribute:: id

    String id for layout.
    
.. attribute:: template

    Template file name or ``None``
    
.. attribute:: default_style

    The default layout style of :class:`UniFormElement` in self.
    One of :ref:`layout types <uniforms-layouts>`. Default ``inlineLabels``.

'''
    def __init__(self, *fields, **kwargs):
        global default_style
        self.id = kwargs.get('id',None)
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
            ctx['html'] = mark_safe(html)
            html = loader.render_to_string(self.template, ctx)
        else:
            html = mark_safe(html)
        
        if self.id:
            return mark_safe('<div id="%s">%s</div>' % (self.id,html))
        else:
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
    __metaclass__ = MediaDefiningClass
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
        return mark_safe(html)


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
            content['content%s' % i] = mark_safe(output)
        return loader.render_to_string(self.template, content)


class Html(UniFormElement):
    '''A :class:`UniFormElement` which renders to `self`.'''
    def __init__(self, html, **kwargs):
        self.html = mark_safe(html)

    def _render(self, form, layout):
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
                 csrf = True,
                 save_as_new  = False,
                 is_ajax = False):
        self.use_csrf_protection = csrf and default_csrf()
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
        self.save_as_new     = save_as_new
        self.prefix          = form.prefix
        self.is_ajax         = is_ajax
        self.error_message   = error_message if error_message is not None else self.default_error_msg
        self.template        = template or self.default_template
        self.add(form,request,instance)
    
    def add(self, form, request = None, instance = None):
        if not form:
            return False
        elif isinstance(form,BaseForm):
            form.layout = getattr(form,'layout',None) or FormLayout()
            instance = instance or getattr(form,'instance',None)
            self._build_fsets(form,request,instance)
            self.forms.append((form.layout,form))
        else:
            form = Html(form)
            self.forms.append((form,form))
        return True
    
    def __len__(self):
        return len(self.forms)
    
    def forms_only(self):
        for form in self.forms:
            if isinstance(form[1],BaseForm):
                yield form[1]
                
    def __getitem__(self, index):
        return self.forms[index][1]
    
    def __get_media(self):
        media = None
        for form in self.forms:
            fmedia = form[1].media
            media = fmedia if media is None else media + fmedia
        return media
    media = property(__get_media)
    
    def __get_instance(self):
        for form in self.forms:
            instance = getattr(form[1],'instance',None)
            if instance:
                return instance
        return None
    instance = property(__get_instance)
    
    def is_valid(self):
        valid = True
        for form in self.forms:
            form = form[1]
            if isinstance(form,BaseForm):
                if not form.is_valid():
                    all = form._errors.get('__all__')
                    if all:
                        if not self._errors:
                            self._errors = all
                        else:
                            self._errors.extend(all)
                    valid = False
        return valid and all_valid(self.formsets)
    
    def save(self, commit = True):
        '''Save the form's content wherever it needs to be stored.
Loops through the forms and call individual save methods if they are
available.

:parameter commit: if ``True`` changes are committed. Default ``True``.'''
        instances = None
        for form in self.forms:
            save = getattr(form[1],'save',None)
            if save:
                instance = save(commit = commit)
        if instance is not None and commit:
            for formset in self.formsets:
                formset.save(instance)
        if instance and getattr(instance,'id',None):
            return instance.__class__.objects.get(id = instance.id)
        else:
            return instance
    
    def add_message(self, request, msg, error = False):
        msg = str(msg)
        if msg:
            if error:
                self._errors.append(msg)
                if not self.is_ajax:
                    messages.error(request,msg)
            else:
                self._messages.append(msg)
                if not self.is_ajax:
                    messages.info(request,msg)
        return self
            
    def force_message(self, request):
        if self.is_ajax:
            for msg in self._messages:
                messages.info(request,msg)
            for msg in self._errors:
                messages.error(request,msg)
            
    def json_message(self):
        msg = self._make_messages('messagelist',self._messages)
        err = self._make_messages('errorlist',self._errors)
        return jhtmls(identifier = '.form-messages', html = msg+err, alldocument = False)
        
    def _formerrors(self, jerr, form):
        for name,errs in form.errors.items():
            errs = str(errs)
            field_instance = form.fields.get(name,None)
            if field_instance:
                bound_field = BoundField(form, field_instance, name)
                jerr.add('#%s-errors' % bound_field.auto_id,errs,alldocument = False)
        
    def json_errors(self, withmessage = True):
        '''Serialize form errors for AJAX-JSON interaction.
        '''
        jerr = jhtmls()
        for form in self.forms:
            form = form[1]
            if isinstance(form,BaseForm):
                self._formerrors(jerr, form)
        for formset in self.formsets:
            for form in formset.forms:
                self._formerrors(jerr, form)
        jerr.update(self.json_message())
        return jerr
    
    @property
    def cleaned_data(self):
        cd = {}
        for form in self.forms:
            cd.update(form[1].cleaned_data)
        return cd

    def render(self, djp = None, validate = False):
        '''Render the uniform by rendering individual forms, inline forms and inputs.'''
        fdict = {}
        forms = []
        num = 0
        inputs = self.render_inputs()
        for layout,form in self.forms:
            num += 1
            html = layout.render(form, inputs)
            forms.append(html)
            fdict['html%s' % num] = html
            
        cd = {'uniform': self,
              'errors': self._errors or '',
              'forms': forms,
              'fdict': fdict,
              'inputs': inputs,
              'inlines': self.render_inlines()}
        
        context_instance = None
        if djp:
            context_instance = RequestContext(djp.request, cd)
            cd = None
            djp.media += self.media
        if validate:
            self.is_valid()
            
        return loader.render_to_string(self.template,cd,
                                       context_instance)
        
    def render_inputs(self):
        if self.inputs:
            c = {'inputs':(mark_safe(s) for s in self.inputs)}
            return loader.render_to_string('djpcms/uniforms/inputs.html',c)
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
        '''Build formsets related to ``instance`` model'''
        formsets = self.formsets
        prefixes = {}
        fp = self.prefix
        if fp:
            fp += '-'
        for inline in form.layout.inlines:
            prefix  = fp + inline.get_default_prefix()
            prefixes[prefix] = p = prefixes.get(prefix, 0) + 1
            if p != 1:
                prefix = "%s-%s" % (prefix, p)
            formset = inline.get_formset(request = request,
                                         data     = form.data,
                                         instance = instance,
                                         prefix   = prefix,
                                         save_as_new = self.save_as_new)
            formsets.append(formset)
    
    def _make_messages(self, cname, mlist):
        if mlist:
            return mark_safe('<ul class="%s"><li>%s</li></ul>' % (cname,'</li><li>'.join(mlist)))
        else:
            return u''
            
    def htmldata(self):
        data = {}
        for form in self.forms:
            data.update(fill_form_data(form[1]))
        for fset in self.formsets:
            formset = fset.formset
            for f in formset.forms:
                data.update(fill_form_data(f))
            data.update(fill_form_data(formset.management_form))
        return data


