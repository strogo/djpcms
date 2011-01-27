from djpcms import sites
from djpcms.utils import merge_dict
from djpcms.template import loader

from .html import TextInput
from .fields import ChoiceField


__all__ = ['autocomplete',
           'AutocompleteForeignKeyInput',
           'AutocompleteManyToManyInput',
           'ModelChoiceField',
           'ModelMultipleChoiceField',
           'set_autocomplete']


class Autocomplete(object):
    '''
    Register a model for autocomplete widget
    Usage, somewhere like urls:
    
    from djpcms.contrib.djpadmin import autocomplete
    
    autocomplete.register(MyModel,['field1,',field2',...])
    '''
    def __init__(self):
        self._register = {}
    
    def register(self, model, view):
        if model not in self._register:
            self._register[model] = view
    
    def get(self, model):
        return self._register.get(model,None)

autocomplete = Autocomplete()


class BaseAutocompleteInput(TextInput):
    attributes = merge_dict(TextInput.attributes,{'model':None,'separator':',','inline':False})
    
    def __init__(self, model, separator = ',', inline = False, attrs = None):
        self.separator = separator
        self.inline = inline
        self.model = model
        self.view  = autocomplete.get(self.model)
        self.search_fields = self.view.appmodel.search_fields
        super(BaseAutocompleteInput,self).__init__(attrs)
        
    def get_url(self):
        if self.view:
            return self.view.get_url()
        else:
            return None


class AutocompleteForeignKeyInput(BaseAutocompleteInput):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """        
    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        if value:
            key = self.search_fields[0].split('__')[0]  
            obj = self.model.objects.get(pk = value)
            label = getattr(obj,key)
        else:
            label = u''
        
        ctx = {'name': name,
               'value': value,
               'label': label,
               'url': self.get_url(),
               'id': attrs.get('id',''),
               'widget_class': self.attrs.pop('class',''),
               'css': sites.settings.HTML_CLASSES}
        
        return loader.render_to_string('djpcms/autocomplete/single.html',ctx)  


class AutocompleteManyToManyInput(BaseAutocompleteInput):    
    """
    A Widget for displaying Mutliple model input in an autocomplete search input 
    instead in a <select> box.
    """
    def value_from_datadict(self, data, files, name):
        if self.inline:
            return data.get(name,None)
        else:
            if isinstance(data, (MultiValueDict, MergeDict)):
                return data.getlist(name)
            return data.get(name, None)        
    
    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        val = ''
            
        value = value or []
        
        if isinstance(value,basestring):
            val = value
        
        selected = []
        ctx = {'items': selected,
               'separator': self.separator,
               'value': val,
               'name': name,
               'url': self.get_url(),
               'id': attrs.get('id',''),
               'widget_class': self.attrs.pop('class',''),
               'css': sites.settings.HTML_CLASSES}
        
        if isinstance(value,list):
            key = self.search_fields[0].split('__')[0]
            for id in value:
                try:
                    obj   = self.model.objects.get(pk=id)
                except:
                    continue
                label = getattr(obj,key)
                selected.append({'label': label,
                                 'name':  name,
                                 'value': obj.id})
        if self.inline:
            stempl = 'multi_inline.html'
        else:
            stempl = 'multi.html'
        return loader.render_to_string('djpcms/autocomplete/%s' % stempl,ctx)


def set_autocomplete(field):
    attrs = field.widget.attrs
    model = field.queryset.model
    view  = autocomplete.get(model)
    if view and view.appmodel.search_fields:
        field.widget = field.auto_class(model,
                                        separator = field.separator,
                                        inline = field.inline,
                                        attrs = attrs)
    return field


class ModelChoiceField(ChoiceField):
    auto_class = AutocompleteForeignKeyInput
    
    def _handle_params(self, query = None, separator = ' ', inline = True, **kwargs):
        self.query = query
        self.separator = separator
        self.inline = inline
        self._raise_error(kwargs)
        
    def __deepcopy__(self, memo):
        result = super(ModelChoiceField,self).__deepcopy__(memo)
        qs = result.queryset
        if hasattr(qs,'__call__'):
            result.queryset = qs()
        return set_autocomplete(result)

            
class ModelMultipleChoiceField(ModelChoiceField):
    auto_class = AutocompleteManyToManyInput
        
    def __deepcopy__(self, memo):
        result = super(ModelMultipleChoiceField,self).__deepcopy__(memo)
        qs = result.queryset
        if hasattr(qs,'__call__'):
            result.queryset = qs()
        return set_autocomplete(result)
