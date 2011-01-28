'''Lightweight form library

Several parts are originally from django
'''
from copy import deepcopy

from djpcms import nodata
from djpcms.utils.collections import OrderedDict
from djpcms.core.orms import mapper
from djpcms.utils.py2py3 import iteritems
from djpcms.utils import force_str
from djpcms.utils.text import nicename

from .globals import *
from .fields import Field
from .html import media_property, FormWidget


__all__ = ['Form',
           'HtmlForm',
           'BoundField',
           'FormSet']


class FormSet(object):
    """A collection of instances of the same Form."""
    creation_counter = 0
    def __init__(self, form_class, prefix = ''):
        self.form_class = form_class
        self.prefix = ''
        self.creation_counter = Field.creation_counter
        FormSet.creation_counter += 1


def get_form_meta_data(bases, attrs, with_base_fields=True):
    """Adapted form django
    """
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)]
    fields = sorted(fields, key=lambda x: x[1].creation_counter)
    
    inlines = [(name, attrs.pop(name)) for name, obj in attrs.items() if isinstance(obj, FormSet)]
    inlines = sorted(inlines, key=lambda x: x[1].creation_counter)
    
    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = base.base_fields.items() + fields
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_fields'):
                fields = base.declared_fields.items() + fields

    return OrderedDict(fields),OrderedDict(inlines)


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        fields,inlines = get_form_meta_data(bases, attrs)
        attrs['base_fields'] = fields
        attrs['base_inlines'] = inlines
        new_class = super(DeclarativeFieldsMetaclass,cls).__new__(cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        return new_class
    

BaseForm = DeclarativeFieldsMetaclass('BaseForm',(object,),{})    


class Form(BaseForm):
    '''base class for forms.'''
    prefix_input = '_prefixed'
    
    def __init__(self, data = None, files = None,
                 initial = None, prefix = None,
                 factory = None, model = None,
                 instance = None, request = None):
        self.is_bound = data is not None or files is not None
        self.factory = factory
        self.rawdata = data
        self._files = files
        self.initial = initial
        self.prefix = prefix or ''
        self.model = model
        self.instance = instance
        self.request = request
        if self.instance:
            model = self.instance.__class__
        self.model = model
        if model:
            self.mapper = mapper(model)            
    
    @property
    def data(self):
        self._unwind()
        return self._data
    
    @property
    def cleaned_data(self):
        self._unwind()
        return self._cleaned_data
        
    @property
    def errors(self):
        self._unwind()
        return self._errors
    
    @property
    def fields(self):
        self._unwind()
        return self._fields
    
    def get_prefix(self, prefix, data):
        if data and self.prefix_input in data:
            return data[self.prefix_input]
        elif prefix:
            if hasattr(prefix,'__call__'):
                prefix = prefix()
            return prefix
        else:
            return ''
    
    def additional_data(self):
        return None
        
    def _unwind(self):
        '''unwind the form by building bound fields and validating if it is bound.'''
        if hasattr(self,'_data'):
            return
        self._data = data = {}
        cleaned = {}
        self._errors = errors = {}
        rawdata = self.additional_data()
        if rawdata:
            rawdata.update(self.rawdata)
        else:
            rawdata = self.rawdata
        self._fields = fields = []
        
        prefix = self.prefix
        initial = self.initial
        is_bound = self.is_bound
        
        # Loop over form fields
        for name,field in iteritems(self.base_fields):
            key = name
            if prefix:
                key = prefix+name
                
            bfield = BoundField(self,field,name,key)
            fields.append(bfield)
            
            if is_bound:
                if key in rawdata:
                    value = rawdata[key]
                else:
                    value = nodata
                try:
                    value = bfield.clean(value)
                    cleaned[name] = value
                except ValidationError as e:
                    errors[name] = force_str(e)
                data[name] = value
            
            elif name in initial:
                data[name] = initial[name]
                
        if is_bound and not errors:
            self._cleaned_data = cleaned
        
            # Invoke the form clean method. Usefull for last minute
            # checking or cross field checking
            try:
                self.clean()
            except ValidationError as e:
                errors['__all__'] = force_str(e)
                del self._cleaned_data
            
    def is_valid(self):
        return self.is_bound and not self.errors
    
    def clean(self):
        pass
    
    def render(self):
        layout = self.factory.layout
        if not layout:
            layout = DefaultLayout()
            self.factory.layout = layout
        return layout.render(self)
    
    def save(self, commit = True):
        '''Save the form. This method works if an instance or a model is available'''
        self.mapper.save(self.cleaned_data, self.instance, commit)
                

class HtmlForm(object):
    '''An HTML class Factory Form'''
    def __init__(self, form_class, layout = None, model = None):
        self.form_class = form_class
        self._layout = layout
        self.model = model
        
    def __get_layout(self):
        layout = self._layout
        if not layout:
            self._layout = layout = DefaultLayout()
        return layout
    def __set_layout(self, lay):
        self._layout = lay
    layout = property(__get_layout,__set_layout)
        
    def __call__(self, model = None, **kwargs):
        return self.form_class(model=model or self.model,**kwargs)
    
    def widget(self, form, **kwargs):
        '''Create a rendable form widget'''
        return FormWidget(form, layout = self.layout, **kwargs)
    
        
class BoundField(object):
    "A Wrapper containg a form, field and data"
    def __init__(self, form, field, name, html_name):
        self.form = form
        self.field = field.copy(self)
        self.name = name
        self.html_name = html_name
        self.value = None
        #self.html_initial_name = form.add_initial_prefix(name)
        #self.html_initial_id = form.add_initial_prefix(self.auto_id)
        if field.label is None:
            self.label = nicename(name)
        else:
            self.label = field.label
        self.help_text = field.help_text
        
    def clean(self, value):
        self.value = self.field.clean(value, self)
        return self.value
        
    def __str__(self):
        return self.as_widget()

    def _errors(self):
        """
        Returns an ErrorList for this field. Returns an empty ErrorList
        if there are none.
        """
        return self.form.errors.get(self.name, self.form.error_class())
    errors = property(_errors)

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        """
        Renders the field by rendering the passed widget, adding any HTML
        attributes passed as attrs.  If no widget is specified, then the
        field's default widget will be used.
        """
        if not widget:
            widget = self.field.widget

        attrs = attrs or {}
        auto_id = self.auto_id
        if auto_id and 'id' not in attrs and 'id' not in widget.attrs:
            if not only_initial:
                attrs['id'] = auto_id
            else:
                attrs['id'] = self.html_initial_id

        if not self.form.is_bound:
            data = self.form.initial.get(self.name, self.field.initial)
            if callable(data):
                data = data()
        else:
            data = self.field.bound_data(
                self.data, self.form.initial.get(self.name, self.field.initial))
        data = self.field.prepare_value(data)

        if not only_initial:
            name = self.html_name
        else:
            name = self.html_initial_name
        return widget.render(name, data, attrs=attrs)

    def _data(self):
        """
        Returns the data for this BoundField, or None if it wasn't given.
        """
        return self.field.widget.value_from_datadict(self.form.data, self.form.files, self.html_name)
    data = property(_data)

    def label_tag(self, contents=None, attrs=None):
        """
        Wraps the given contents in a <label>, if the field has an ID attribute.
        Does not HTML-escape the contents. If contents aren't given, uses the
        field's HTML-escaped label.

        If attrs are given, they're used as HTML attributes on the <label> tag.
        """
        contents = contents or conditional_escape(self.label)
        widget = self.field.widget
        id_ = widget.attrs.get('id') or self.auto_id
        if id_:
            attrs = attrs and flatatt(attrs) or ''
            contents = u'<label for="%s"%s>%s</label>' % (widget.id_for_label(id_), attrs, unicode(contents))
        return mark_safe(contents)

    def css_classes(self, extra_classes=None):
        """
        Returns a string of space-separated CSS classes for this field.
        """
        if hasattr(extra_classes, 'split'):
            extra_classes = extra_classes.split()
        extra_classes = set(extra_classes or [])
        if self.errors and hasattr(self.form, 'error_css_class'):
            extra_classes.add(self.form.error_css_class)
        if self.field.required and hasattr(self.form, 'required_css_class'):
            extra_classes.add(self.form.required_css_class)
        return ' '.join(extra_classes)

    def _is_hidden(self):
        "Returns True if this BoundField's widget is hidden."
        return self.field.widget.is_hidden
    is_hidden = property(_is_hidden)

    def _auto_id(self):
        """
        Calculates and returns the ID attribute for this BoundField, if the
        associated Form has specified auto_id. Returns an empty string otherwise.
        """
        auto_id = self.form.auto_id
        if auto_id and '%s' in smart_unicode(auto_id):
            return smart_unicode(auto_id) % self.html_name
        elif auto_id:
            return self.html_name
        return ''
    auto_id = property(_auto_id)
