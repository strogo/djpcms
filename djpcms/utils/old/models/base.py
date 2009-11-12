
from django.db import models
from django.utils.text import capfirst
from django.utils.encoding import force_unicode

from qmpy.python.retargs import errorArg, Result
from django.contrib.auth.models import User, AnonymousUser , Group

__all__ = ['unique_code_name',
           'get_admin',
           'get_admin_form',
           'dolog',
           'get_model_list',
           'getobject',
           'getcode']


def _try_unique_code_name(m, name):
    '''
    Utility function which test whether model 'm' has a unique field with name 'name'
     m    model to test
     name field to test
    '''
    opts = m._meta
    try:
        attr = opts.get_field(name)
        if not attr.unique:
            return None
        return name
    except:
        return None


def _try_attribute_code_name(m,name):
    try:
        attr = getattr(m,name)
        if callable(attr):
            attr = attr()
        return name
    except:
        return None


def unique_code_name(m):
    opts = m._meta
    code = _try_unique_code_name(m,'code')
    if code == None:
        code = _try_attribute_code_name(m,'code')
        if code == None:
            code = _try_unique_code_name(m,'user')
            if code == None:
                return opts.pk.attname
            else:
                return code
        else:
            return code
    else:
        return code


def getobject(model,code):
    try:
        return model.objects.select_related().get(code=code)
    except:
        user = get_user(code)
        if user.preference == None:
            return model.objects.select_related().get(pk=code)
        else:
            return self.preference

def getcode(obj):
    try:
        return obj.code
    except:
        try:
            return obj.username
        except:
            return obj.id


def _get_admin(model):
    from djangosite.contrib import admin
    try:
        return admin.site._registry[model]
    except KeyError:
        return None


def get_admin(model):
    '''
    Get the Admin site object if it exists
    '''
    if isinstance(model,models.Model):
        return _get_admin(model._default_manager.model)
    else:
        return _get_admin(model)
    
def get_admin_form(model, request, **kwargs):
    obj = None
    if isinstance(model,models.Model):
        obj   = model
        model = obj._default_manager.model
    admin = _get_admin(model)
    if admin:
        return admin.get_form(request, obj = obj, **kwargs)
    else:
        return None


def dolog(obj,user,flag,msg):
    '''
    Log an action into the database.
    Return a 3-elements tuple a
        a[0] is True if everything is fine otherwise the error will be in a[2]
        a[1] is the object to be logged
    '''
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.admin.models import LogEntry
    try:
        pk_value = obj._get_pk_val()
        model    = obj.__class__
        id       = user.id
        LogEntry.objects.log_action(id,
                                    ContentType.objects.get_for_model(model).id,
                                    pk_value,
                                    force_unicode(obj),
                                    flag,
                                    msg)
        # TODO: make this more general
        pkn   = unique_code_name(obj)
        field = obj._meta.get_field(pkn)
        code  = getattr(obj, field.attname)
        return Result(result = code)
    except Exception, e:
        return errorArg(error = e, result = obj)



def get_model_list(app_label, app_models):
    '''
    Return a list of model in application app_label
    '''
    model_list = []
    for model in app_models:
        opts = model._meta
        try:
            if not model.show_in_dblist:
                continue
        except:
            pass
        adm = get_admin(model)
        
        if adm:
            code = model.__name__.lower()
            args = {'model': model,
                    'name':  capfirst(opts.verbose_name_plural),
                    'code':  code}
            model_list.append(model)
    return model_list



