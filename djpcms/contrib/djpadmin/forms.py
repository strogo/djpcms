from django import forms
from django.utils.safestring import mark_safe

from django.conf import settings


basemedia          = '%sdjpadmin' % settings.MEDIA_URL
base_plugin        = '%s/jquery-autocomplete' % basemedia
autocomplete_class = 'djp-autocomplete'
ADMIN_URL_PREFIX   = getattr(settings,"ADMIN_URL_PREFIX","/admin/")


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
                    '%s/autocomplete.js ' % basemedia
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
        sf = ''.join(['<span>%s</span>' % s for s in self.search_fields])
        meta = self.rel.to._meta
        url = '%s%s/%s/' % (ADMIN_URL_PREFIX,meta.app_label,meta.module_name)
        return mark_safe(u'''
<div class="%(klass)s">
<input type="text" id="lookup_%(name)s" value="%(label)s" size="40"/>
 <dim style="display:none">
  <input type="text" name="%(name)s">
  <a href="%(url)s"></a>
  %(span)s
 </div>
</div>
            ''' % {
                   'label': label,
                   'name': name,
                   'value': value,
                   'span': sf,
                   'url': url,
                   'klass': autocomplete_class
                   })


class ModelChoiceField(forms.ModelChoiceField):
    
    def __init__(self, queryset, search_fields, widget = None, **kwargs):
        self.widget = widget or AutocompleteForeignKeyInput(queryset, search_fields)
        super(ModelChoiceField,self).__init__(queryset, **kwargs)

