'''Lightweight form library

Several parts are originally from django
'''
from djpcms.utils.collections import OrderedDict
from djpcms.utils.py2py3 import iteritems

from .globals import *
from .fields import Field
from .html import media_property


__all__ = ['Form',
           'HtmlForm',
           'BoundField']


def get_declared_fields(bases, attrs, with_base_fields=True):
    """Adapted form djago
    """
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)]
    fields.sort(key=lambda x: x[1].creation_counter)

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

    return OrderedDict(fields)


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = get_declared_fields(bases, attrs)
        new_class = super(DeclarativeFieldsMetaclass,cls).__new__(cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        return new_class
    

BaseForm = DeclarativeFieldsMetaclass('BaseForm',(object,),{})    


class Form(BaseForm):
    '''base class for forms. This class is created by instances
of a :class:`Factory`'''
    prefix_input = '_prefixed'
    
    def __init__(self, data = None, files = None,
                 initial = None, prefix = None,
                 factory = None):
        self.is_bound = data is not None or files is not None
        self.factory = factory
        self.rawdata = data
        self._files = files
        self.initial = initial
        self.prefix = prefix or ''
    
    @property
    def data(self):
        self._validate()
        return self._data

    @property
    def cleaned_data(self):
        self._validate()
        return self._cleaned_data
        
    @property
    def errors(self):
        self._validate()
        return self._errors
    
    @property
    def fields(self):
        self._validate()
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
        
    def _validate(self):
        if hasattr(self,'_data'):
            return
        self._data = data = {}
        cleaned = {}
        self._errors = errors = {}
        tempdata = self.rawdata.copy()
        self._fields = fields = []
        
        prefix = self.prefix
        np = len(prefix) 
        initial = self.initial
        
        for name,field in iteritems(self.base_fields):
            key = name
            if prefix:
                key = prefix+name
            fields.append(BoundField(self,field,name,key))
            
            if self.is_bound:
                try:
                    value = field.clean(tempdata.pop(key,nodata))
                    cleaned[name] = value
                except ValidationError:
                    errors.append(field)
                data[name] = value
            
            elif name in initial:
                data[name] = initial[name]
            
    def is_valid(self):
        return self.is_bound and not self.errors
    
    def render(self):
        layout = self.factory.layout
        if not layout:
            layout = DefaultLayout()
            self.factory.layout = layout
        return layout.render(self)



class HtmlForm(object):
    
    def __init__(self, form_class, layout = None, model = None):
        self.form_class = form_class
        self.layout = layout
        self.model = model
        
    
        
class BoundField(object):
    "A Field plus data"
    def __init__(self, form, field, name, html_name):
        self.form = form
        self.field = field
        self.name = name
        self.html_name = html_name
        #self.html_initial_name = form.add_initial_prefix(name)
        #self.html_initial_id = form.add_initial_prefix(self.auto_id)
        #if self.field.label is None:
        #    self.label = pretty_name(name)
        #else:
        #    self.label = self.field.label
        self.help_text = field.help_text

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

    def as_text(self, attrs=None, **kwargs):
        """
        Returns a string of HTML for representing this as an <input type="text">.
        """
        return self.as_widget(TextInput(), attrs, **kwargs)

    def as_textarea(self, attrs=None, **kwargs):
        "Returns a string of HTML for representing this as a <textarea>."
        return self.as_widget(Textarea(), attrs, **kwargs)

    def as_hidden(self, attrs=None, **kwargs):
        """
        Returns a string of HTML for representing this as an <input type="hidden">.
        """
        return self.as_widget(self.field.hidden_widget(), attrs, **kwargs)

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
