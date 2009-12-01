from django.utils import simplejson as json

from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

class ajaxhtml(object):
    
    def __new__(cls):
        obj = super(ajaxhtml,cls).__new__(cls)
        d = {}
        obj._dict = d
        
        # AJAX classes
        d['post_view_key']           = 'xhr'
        d['ajax']                    = 'ajax'
        d['errorlist']               = 'errorlist'
        d['formmessages']            = 'form-messages'
        d['field_separator']         = 'field-separator'
        
        # css decorators
        d['calendar_class']          = 'calendar-input'
        d['currency_input']          = 'currency-input'
        d['edit']                    = 'editable'
        d['delete']                  = 'deletable'
        d['secondary_in_list']       = 'secondary'
        d['link_selected']           = 'selected'
        
        return obj
    
    def __init__(self):
        d = self._dict
        for k,v in d.iteritems():
            setattr(self,k,v)
    
    def __setitem__(self, k, v):
        self._dict[k] = v

    def tojson(self):
        return mark_safe(force_unicode(json.dumps(self._dict)))
    

