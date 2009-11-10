__doc__ = '''Several utilities for displaying data from application models'''

from django.conf import settings
from django.db import models
from django.utils import dateformat
from django.utils.translation import get_date_formats
from django.utils.text import capfirst
from django.utils.html import escape

from qmpy.python.nuts import isnumeric

__all__ = ['_boolean_icon',
           'trim',
           'hascode',
           'datetime_repr',
           'field_header',
           'field_repr',
           'field_value']


def _boolean_icon(field_val):
    BOOLEAN_MAPPING = {True: 'yes', False: 'no', None: 'unknown'}
    return '<img src="%simg/admin/icon-%s.gif" alt="%s" />' % (settings.MEDIA_URL, BOOLEAN_MAPPING[field_val], field_val)

def trim(val):
    from decimal import Decimal
    if isinstance(val,Decimal):
        return str(val)
    elif isnumeric(val):
        return val
    else:
        return str(val)

def hascode(model,code='code'):
    try:
        f = model._meta.get_field(code)
        if f.unique:
            return True
        else:
            return False
    except models.FieldDoesNotExist:
        return False


def datetime_repr(date):
    (date_format, datetime_format, time_format) = get_date_formats()
    return capfirst(dateformat.format(date, datetime_format))
    

def field_header(model,field_name):
    '''
    This function returns a tuple for a field_name containing
     header (the field verbose name)
     sortable (true or false)
    '''
    opts = model._meta
    try:
        attr = opts.get_field(field_name)
        header = attr.verbose_name
        sortable = True
    except models.FieldDoesNotExist:
        # For non-field list_display values, check for the function
        # attribute "short_description". If that doesn't exist, fall back
        # to the method name. And __str__ and __unicode__ are special-cases.
        if field_name == '__unicode__' or field_name == '__str__':
            header = opts.verbose_name
        else:
            attr = getattr(model, field_name) # Let AttributeErrors propagate.
            try:
                header = attr.short_description
            except AttributeError:
                header = field_name
            try:
                sortable = attr.sortable_field
            except:
                sortable = True
    header = capfirst(header.replace('_',' '))   
    return (header,sortable)


def field_repr(result, f, NoneType= '(None)'):
    '''
    This function return a representation for field 'f' in model 'result'.
    Used in qmpy.django.table.field_value function
    '''
    field_val = getattr(result, f.attname)

    if isinstance(f.rel, models.ManyToOneRel):
        if field_val is not None:
            result_repr = escape(getattr(result, f.name))
        else:
            result_repr = NoneType
    #
    # Dates and times are special: They're formatted in a certain way.
    elif isinstance(f, models.DateField) or isinstance(f, models.TimeField):
        if field_val:
            return str(field_val)
            #(date_format, datetime_format, time_format) = get_date_formats()
            #if isinstance(f, models.DateTimeField):
            #    result_repr = capfirst(dateformat.format(field_val, datetime_format))
            #elif isinstance(f, models.TimeField):
            #    result_repr = capfirst(dateformat.time_format(field_val, time_format))
            #else:
            #    result_repr = capfirst(dateformat.format(field_val, date_format))
        else:
            result_repr = NoneType
        row_class = ' class="nowrap"'
    #
    # Booleans are special: We use images.
    elif isinstance(f, models.BooleanField) or isinstance(f, models.NullBooleanField):
        result_repr = _boolean_icon(field_val)
    #
    # DecimalFields are special: Zero-pad the decimals.
    elif isinstance(f, models.DecimalField):
        if field_val is not None:
            result_repr = ('%%.%sf' % f.decimal_places) % field_val
        else:
            result_repr = NoneType
    #
    # Fields with choices are special: Use the representation
    # of the choice.
    elif f.choices:
        result_repr = dict(f.choices).get(field_val, NoneType)
    else:
        result_repr = escape(field_val)
        
    return result_repr


def field_value(obj, field_name, NoneValue=None):
    '''
    Given an object 'obj' and a field_name
    this function return a tuple with
    field_verbose_name, field_value
    '''
    try:
        f = obj._meta.get_field(field_name)
        field_val = field_repr(obj, f, NoneValue)
        #field_val = getattr(obj, f.attname)
        fname = f.verbose_name
        try:
            fname = str(fname._proxy____args[0])
        except:
            fname = str(fname)
    except models.FieldDoesNotExist:
        fname = field_name.replace('_', ' ')
        try:
            field_val = getattr(obj, field_name)
            if callable(field_val):
                try:
                    fname = field_val.short_description
                except AttributeError:
                    pass
                field_val = field_val()
        except:
            field_val = NoneValue
            
    field_val = trim(field_val)
    if type(field_val) == bool:
        field_val = _boolean_icon(field_val)
    return fname, field_val