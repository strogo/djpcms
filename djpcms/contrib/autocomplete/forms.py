from django import forms
from django.utils.safestring import mark_safe

from django.conf import settings


basemedia   = '%sautocomplete' % settings.MEDIA_URL
base_plugin = '%s/jquery-autocomplete' % basemedia


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
        rendered = super(AutocompleteForeignKeyInput, self).render(name, value, attrs)
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
            return rendered + mark_safe(u'''
<input type="text" id="lookup_%(name)s" value="%(label)s" size="40"/>
            ''' % {
                   'label': label,
                   'name': name,
                   'value': value
                   })