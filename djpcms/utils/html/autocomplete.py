from django import forms
from django.template import loader
from django.utils.datastructures import MultiValueDict, MergeDict
from django.db import models
from django.utils.safestring import mark_safe
from djpcms.conf import settings


__all__ = ['autocomplete',
           'AutocompleteForeignKeyInput',
           'AutocompleteManyToManyInput',
           'ModelChoiceField',
           'ModelMultipleChoiceField']


class Autocomplete(object):
    '''
    Register a model for autocomplete widget
    Usage, somewhere like urls:
    
    from djpcms.contrib.djpadmin import autocomplete
    
    autocomplete.register(MyModel,['field1,',field2',...])
    '''
    def __init__(self):
        self._register = {}
    
    def register(self, model, search_list):
        if model not in self._register:
            self._register[model] = search_list
    
    def get(self, model):
        return self._register.get(model,None)

autocomplete = Autocomplete()


basemedia                = 'djpcms'
base_plugin              = '%s/jquery-autocomplete' % basemedia
autocomplete_class       = 'djp-autocomplete'
multi_autocomplete_class = '%s multi' % autocomplete_class
ADMIN_URL_PREFIX         = getattr(settings,"ADMIN_URL_PREFIX","/admin/")


class BaseAutocompleteInput(forms.TextInput):
    class_for_form = forms.TextInput
    
    def __init__(self, model, search_fields, attrs=None):
        self.model = model
        self.search_fields = search_fields
        super(BaseAutocompleteInput, self).__init__(attrs)
        
    def get_url(self):
        meta = self.model._meta
        return '%s%s/%s/' % (ADMIN_URL_PREFIX,meta.app_label,meta.module_name)
    
    class Media:
            css = {
                    'all': ('%s/jquery.autocomplete.css' % base_plugin,)
            }
            js = (
                    '%s/jquery.autocomplete.js' % base_plugin,
                    '%s/autocomplete.js' % basemedia
                )


class AutocompleteForeignKeyInput(BaseAutocompleteInput):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """
    #def label_for_value(self, value, name):
    #    rel_name = self.search_fields[0].split('__')[0]
    #    key = self.rel.get_related_field().name
    #    obj = self.rel.to._default_manager.get(**{key: value})
    #    return getattr(obj,rel_name)

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
               'css': settings.HTML_CLASSES}
        
        return loader.render_to_string('djpcms/autocomplete/single.html',ctx)  


class AutocompleteManyToManyInput(BaseAutocompleteInput):    
    """
    A Widget for displaying Mutliple model input in an autocomplete search input 
    instead in a <select> box.
    """
    def __init__(self, *args, **kwargs):
        self.separator = kwargs.pop('separator',',')
        self.inline    = kwargs.pop('inline',False)
        super(AutocompleteManyToManyInput,self).__init__(*args, **kwargs)
    
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
               'css': settings.HTML_CLASSES}
        
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


class ModelChoiceField(forms.ModelChoiceField):
    
    def __init__(self, queryset, widget = None, **kwargs):
        if not widget:
            model = queryset.model
            search_fields = autocomplete.get(model)
            if search_fields:
                widget = AutocompleteForeignKeyInput(model, search_fields)
                self.widget = widget
        super(ModelChoiceField,self).__init__(queryset, widget = widget, **kwargs)
            
class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    
    def __init__(self, queryset, widget = None, **kwargs):
        if not widget:
            model = queryset.model
            search_fields = autocomplete.get(model)
            if search_fields:
                widget = AutocompleteManyToManyInput(model, search_fields)
                self.widget = widget
        super(ModelMultipleChoiceField,self).__init__(queryset, widget = widget, **kwargs)
