import datetime
from django.db import models
from django.utils.encoding import smart_unicode, iri_to_uri
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.utils.safestring import mark_safe

from base import unique_code_name


__all__ = ['make_filter']


def make_filter(f):
    for test, factory in _tests:
        if test(f):
            f = factory(f)
            if type(f) == list:
                return f
            else:
                return [f]
    return None
    

class FilterSpec(object):
    filter_specs = []
    
    def __init__(self, f):
        self.field   = f
        self.recode  = '([^/]+)'
        self.model   = None
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__,self.name)
    
    def __get_name(self):
        return self.field.name
    name = property(fget = __get_name)
    
    def valuecode(self, arg):
        pass

    def choices(self):
        raise NotImplementedError()

    def title(self):
        return self.field.verbose_name

    def output(self, cl):
        return False
    

class RelatedFilterSpec(FilterSpec):
    
    def __init__(self, f):
        super(RelatedFilterSpec, self).__init__(f)
        self.model = self.field.rel.to
        if isinstance(f, models.ManyToManyField):
            self.lookup_title = f.rel.to._meta.verbose_name
        else:
            self.lookup_title = f.verbose_name

    def title(self):
        return self.lookup_title
    
    def valuecode(self, arg):
        m    = self.model
        code = unique_code_name(m)
        if isinstance(arg,m):
            obj       = arg
            valuecode = getattr(arg,code)
        else:
            valuecode = arg
            kw        = {code: valuecode}
            obj       = m.objects.get(**kw)
        return code, valuecode, obj
    
    def choices(self):
        return self.model._default_manager.all()


class ChoicesFilterSpec(FilterSpec):
    
    def __init__(self, f):
        super(ChoicesFilterSpec, self).__init__(f)
        self.lookup_kwarg = '%s__exact' % f.name



def datefieldgenerator(f):
    date_from = DateFieldFilterSpec(f)
    date_to   = DateFieldFilterSpec(f)
    return [date_from,date_to]



class DateFieldFilterSpec(FilterSpec):
    
    def __init__(self, f, model, model_admin):
        super(DateFieldFilterSpec, self).__init__(f)



class BooleanFieldFilterSpec(FilterSpec):
    
    def __init__(self, f):
        super(BooleanFieldFilterSpec, self).__init__(f)

    def choices(self):
        return [True,False]

class AllValuesFilterSpec(FilterSpec):
    
    def __init__(self, f):
        super(AllValuesFilterSpec, self).__init__(f)
        


def make_tests():
    global _tests
    if not _tests:
        _tests.append((lambda f: bool(f.rel),     RelatedFilterSpec))
        _tests.append((lambda f: bool(f.choices), ChoicesFilterSpec))
        _tests.append((lambda f: isinstance(f, models.DateField), datefieldgenerator))
        _tests.append((lambda f: isinstance(f, models.BooleanField) or isinstance(f, models.NullBooleanField), BooleanFieldFilterSpec))
        _tests.append((lambda f: True, AllValuesFilterSpec))

_tests = []
make_tests()


        