"""
A custom Model Field for djpcms.
"""
import json
from django.db import models

from djpcms.utils import JSONDateDecimalEncoder, date_decimal_hook, slugify

try:
    import cPickle as pickle
except ImportError:
    import pickle
    


def compact(data, sep = '_'):
    if not sep:
        return data
    d = {}
    for k,v in data.items():
        rdata = d
        keys = k.split(sep)
        for key in keys[:-1]:
            kd = rdata.get(key,None)
            if kd is None:
                kd = {}
                rdata[key] = kd
            rdata = kd
        rdata[keys[-1]] = v
    return d


class SlugCode(models.CharField):
    
    def __init__(self, rtxchar='-', lower=False, upper = False, **kwargs):
        '''
        @param lower: boolean, if true the field will be converted to lower case
        @param upper: boolen if lower is False and this is True the field will be converted to upper cases 
        '''
        self.rtxchar = u'%s' % rtxchar
        self.lower   = lower
        self.upper   = upper
        super(SlugCode,self).__init__(**kwargs)
        
    def trim(self, value):
        value = slugify(u'%s'%value, rtx = self.rtxchar)
        if self.lower:
            value = value.lower()
        elif self.upper:
            value = value.upper()
        return value
        
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        value = self.trim(value)
        setattr(model_instance, self.attname, value)
        return value


class JSONField(models.TextField):
    # need to add this otherwise to_python() is not called
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        kwargs['default'] = kwargs.get('default','{}')
        self.encoder_class = kwargs.pop('encoder_class',JSONDateDecimalEncoder)
        self.decoder_hook  = kwargs.pop('decoder_hook',date_decimal_hook)
        self.sep = kwargs.pop('sep',None)
        super(JSONField,self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""
        if isinstance(value, basestring):
            if not value:
                value = {}
            else:
                value = json.loads(value, object_hook = self.decoder_hook)
        return value
 
    def get_prep_value(self, value):
        if value is None:
            return
        return json.dumps(compact(value,self.sep), cls=self.encoder_class)
 
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


class PickledObject(str):
    """A subclass of string so it can be told whether a string is
       a pickled object or not (if the object is an instance of this class
       then it must [well, should] be a pickled one)."""
    pass


class PickledObjectField(models.Field):
    __metaclass__ = models.SubfieldBase
    
    def to_python(self, value):
        if isinstance(value, PickledObject):
            # If the value is a definite pickle; and an error is raised in de-pickling
            # it should be allowed to propogate.
            return pickle.loads(str(value))
        else:
            try:
                return pickle.loads(str(value))
            except:
                # If an error was raised, just return the plain value
                return value
    
    def get_prep_value(self, value):
        if value is not None and not isinstance(value, PickledObject):
            value = PickledObject(pickle.dumps(value))
        return value
    
    def get_internal_type(self): 
        return 'TextField'
    
    #def get_prep_lookup(self, lookup_type, value):
    #    if lookup_type == 'exact':
    #        value = self.get_db_prep_save(value)
    #        return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
    #    elif lookup_type == 'in':
    #        value = [self.get_db_prep_save(v) for v in value]
    #        return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value)
    #    else:
    #        raise TypeError('Lookup type %s is not supported.' % lookup_type)



# Add south support if south is installed
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^djpcms\.fields\.SlugCode"])
    add_introspection_rules([], ["^djpcms\.fields\.JSONField"])
except:
    pass
