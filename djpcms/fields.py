import re
import unicodedata

from django.db import models
from django import forms
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from django.core.exceptions import ObjectDoesNotExist


ALL_DATE_INPUT_FORMATS = (
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
    '%a %d %b %Y',                      # 'Wed 25 Oct 2006'
)

def get_ajax():
    from djpcms.settings import HTML_CLASSES
    return HTML_CLASSES


class NewUserName(forms.CharField):
    
    default_error_messages = {
        'required': u"Please enter a username.",
        'notavailable': u"%s is not available. Please choose a different username.",
        'max_length': u'Ensure username has at most %(max)d characters',
        'max_length': u'Ensure username has at least %(min)d characters',
    }

    def __init__(self, lower = True, *args, **kwargs):
        self.lower = lower
        super(NewUserName,self).__init__(*args, **kwargs)
    
    def clean(self, value):
        from django.contrib.auth.models import User
        username = super(NewUserName,self).clean(value)
        if self.lower:
            username = username.lower()
            
        try:
            user = User.objects.get(username = username)
        except ObjectDoesNotExist:
            # Good, the username is not available, lets use it
            pass
        else:
            raise forms.ValidationError(self.error_messages['notavailable'] % username)
        return username


class UniqueEmail(forms.EmailField):
    
    default_error_messages = {
        'required': u"Please enter a valid email address.",
        'invalid': u"Please enter a valid email address.",
        'notavailable': u"Already in use. Choose a different email.",
    }

    def __init__(self, *args, **kwargs):
        super(UniqueEmail,self).__init__(*args, **kwargs)
    
    def clean(self, value):
        from django.contrib.auth.models import User
        email = super(UniqueEmail,self).clean(value)
        email = email.lower()
        user = User.objects.filter(email = email)
        if not user.count():
            # Good, the username is not available, lets use it
            pass
        else:
            raise forms.ValidationError(self.error_messages['notavailable'])
        return email


class TradeDateField(forms.DateField):
    
    def __init__(self, *args, **kwargs):
        d  = {'class':get_ajax().calendar_class}
        wdg = forms.TextInput(d)
        self.dateformat = get_ajax().date_format
        input_formats   = ALL_DATE_INPUT_FORMATS
        super(TradeDateField,self).__init__(widget = wdg,
                                            input_formats = input_formats,
                                            *args, **kwargs)

class NullDateField(TradeDateField):
    
    def __init__(self, *args, **kwargs):
        kwargs.pop('required',None)
        super(NullDateField,self).__init__(required = False, *args, **kwargs)
        
    def clean(self, value):
        c = super(NullDateField,self).clean(value)
        return c
    
    
class UniqueCodeField(forms.CharField):
    
    def __init__(self, model = None, codename = 'code', lower = True, rtf = '_', extrafilters = None, *args, **kwargs):
        self.model = model
        self.lower = lower
        self.rtf   = rtf
        self.extrafilters = extrafilters
        self.codename     = codename
        super(UniqueCodeField,self).__init__(*args, **kwargs)
        
    def clean(self, value):
        c = super(UniqueCodeField,self).clean(value)
        if self.model:
            c = self.trimcode(c)
            kwargs = self.extrafilters or {}
            kwargs[self.codename] = c
            obj = self.model.objects.filter(**kwargs)
            if obj.count():
                raise forms.ValidationError('%s with %s code already available' % (self.model,c))
        return c
    
    def trimcode(self, c):
        return slugify(c, lower = self.lower, rtx = self.rtf)


class ModelCharField(forms.CharField):
    
    def __init__(self, model, fieldname, extrafilters = None, *args, **kwargs):
        self.model       = model
        self.model_field = None
        for field in model._meta.fields:
            if field.attname == fieldname:
                self.model_field = field
                break
        if not self.model_field:
            raise ValueError('field %s not available in model %s' % (fieldname,model))
        if not isinstance(self.model_field,models.CharField):
            raise ValueError('field %s not char field in model %s' % (fieldname,model))
        self.extrafilters = extrafilters
        super(ModelCharField,self).__init__(*args, **kwargs)
        
    def clean(self, value):
        value = super(ModelCharField,self).clean(value)
        fieldname = self.model_field.attname
        try:
            value = value[:self.model_field.max_length]
        except:
            value = value
        value = self.trim(value)
        if self.model_field._unique:
            kwargs = self.extrafilters or {}
            kwargs[fieldname] = value
            obj = self.model.objects.filter(**kwargs)
            if obj.count():
                raise forms.ValidationError('%s code already available' % value)
        return value
        
    def trim(self, value):
        return value

class SlugField(ModelCharField):
    
    def __init__(self, *args, **kwargs):
        super(SlugField,self).__init__(*args, **kwargs)
        
    def trim(self, value):
        return self.model_field.trim(value)        
    


class AjaxChoice(forms.ChoiceField):
    
    def __init__(self, *args, **kwargs):
        super(AjaxChoice,self).__init__(*args, **kwargs)
        
    def widget_attrs(self, widget):
        return {'class': get_ajax().ajax}

class AjaxModelChoice(forms.ModelChoiceField):
    
    def __init__(self, *args, **kwargs):
        super(AjaxModelChoice,self).__init__(*args, **kwargs)
        
    def widget_attrs(self, widget):
        return {'class': get_ajax().ajax}

        
class CurrencyField(forms.DecimalField):
    
    def __init__(self, *args, **kwargs):
        d  = {'class':classes.currency_input}
        wdg = forms.TextInput(attrs=d)
        super(CurrencyField,self).__init__(widget = wdg, *args, **kwargs)
    
    def clean(self, value):
        try:
            value = str(value)
            vals = []
            for v in value:
                if v == ' ' or v == ',':
                    continue
                vals.append(v)
            sv = ''.join(vals)
        except:
            sv = None
        return super(CurrencyField,self).clean(sv)
    

class AjaxAutocompleteWidget(forms.Widget):
    input_type = 'text'
    
    def __init__(self,
                 url = None,
                 ajaxclass = get_ajax().ajax_autocomplete,
                 attr = None):
        if url is None:
            raise TypeError("Keyword argument 'url' must be supplied")
        self.url      = url
        self.cssclass = ajaxclass
        super(AjaxAutocompleteWidget,self).__init__(attr)
        
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        url = force_unicode(self.url)
        html = ['<div class="%s">' % self.cssclass,
                '<input%s />' % flatatt(final_attrs),
                '<a href="%s" style="display: none"></a>' % url,
                '</div>']
        return mark_safe(u'%s' % '\n'.join(html))
    
    
class AjaxAutocomplete(forms.CharField):
    
    def __init__(self, url = None, widget = None, *args, **kwargs):
        if widget is None:
            widget = AjaxAutocompleteWidget(url = url)
        if not isinstance(widget, AjaxAutocompleteWidget):
            raise TypeError("Keyword widget must be a AjaxAutocompleteWidget")
        super(AjaxAutocomplete,self).__init__(widget = widget, *args, **kwargs)
        
