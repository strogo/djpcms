from django import forms
from django.template import loader
from django.utils.datastructures import MultiValueDict, MergeDict
from django.db import models
from django.utils.safestring import mark_safe
from djpcms.conf import settings


__all__ = ['autocomplete',
           'AutocompleteForeignKeyInput',
           'AutocompleteManyToManyInput',
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


class AutocompleteForeignKeyInput(forms.HiddenInput):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """
    def __init__(self, rel, search_fields, attrs=None):
        self.rel = rel
        self.search_fields = search_fields
        super(AutocompleteForeignKeyInput, self).__init__(attrs)
                
    class Media:
            css = {
                    'all': ('%s/jquery.autocomplete.css' % base_plugin,)
            }
            js = (
                    '%s/jquery.autocomplete.js' % base_plugin,
                    '%s/autocomplete.js' % basemedia
                )

    def label_for_value(self, value):
        rel_name = self.search_fields[0].split('__')[0]
        key = self.rel.get_related_field().name
        obj = self.rel.to._default_manager.get(**{key: value})
        return getattr(obj,rel_name)

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        meta = self.rel.to._meta
        url = '%s%s/%s/' % (ADMIN_URL_PREFIX,meta.app_label,meta.module_name)
        return mark_safe(u'''
<div class="%(klass)s">
<input type="text" id="lookup_%(name)s" value="%(label)s" size="40"/>
 <div style="display:none">
  <input type="text" name="%(name)s" value="%(value)s">
  <a href="%(url)s"></a>
 </div>
</div>
            ''' % {
                   'label': label,
                   'name': name,
                   'value': value,
                   'url': url,
                   'klass': autocomplete_class
                   })




class AutocompleteManyToManyInput(forms.TextInput):    
    """
    A Widget for displaying Mutliple model input in an autocomplete search input 
    instead in a <select> box.
    """
    class_for_form = forms.TextInput
    
    def __init__(self, model, search_fields, attrs=None):
        self.model = model
        self.search_fields = search_fields
        super(AutocompleteManyToManyInput, self).__init__(attrs)
                
    class Media:
            css = {
                    'all': ('%s/jquery.autocomplete.css' % base_plugin,)
            }
            js = (
                    '%s/jquery.autocomplete.js' % base_plugin,
                    '%s/autocomplete.js' % basemedia
                )

    def get_url(self):
        meta = self.model._meta
        return '%s%s/%s/' % (ADMIN_URL_PREFIX,meta.app_label,meta.module_name)
    
    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)        
    
    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        value = value or []
            
        selected = []
        ctx = {'items': selected,
               'name': name,
               'url': self.get_url(),
               'id': attrs.get('id',''),
               'widget_class': self.attrs.pop('class',''),
               'css': settings.HTML_CLASSES}
        
        if value:
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
                
        return loader.render_to_string('djpcms/autocomplete/multi.html',ctx)
    
    
# a new ModelMultipleChoiceField
#
class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    
    def __init__(self, queryset, widget = None, **kwargs):
        if not widget:
            model = queryset.model
            search_fields = autocomplete.get(model)
            if search_fields:
                widget = AutocompleteManyToManyInput(model, search_fields)
                self.widget = widget
        super(ModelMultipleChoiceField,self).__init__(queryset, widget = widget, **kwargs)

