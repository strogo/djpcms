
from django.db import models
import log

__all__ = ['Pmodel','get_codevalue']


def get_codevalue(val):
    if isinstance(val,Pmodel):
        code = unique_code_name(val)
        return getattr(val, code)
    else:
        return str(val)


class Pmodel(models.Model):
    
    class Meta:
        abstract = True
        
    def save_and_log(self, user, msg='', flag = None):
        return log.save_and_log(self, user, msg, flag)

    def delete_and_log(self, user, msg=''):
        return log.delete_and_log(self,user,msg)


class pmodel_old(models.Model):
    '''
    Base class for models.
    This model expand django model functionality with some
    useful addons
    '''
    show_in_dblist = True
    def jtable(self, post_params = None, NoneType = None):
        return _jtable_from_model(self,post_params,NoneType)
    
    def _unique_code_name(self):
        return unique_code_name(self)
    
    def __get_unique_codename(self):
        return self._unique_code_name()
    codename = property(fget = __get_unique_codename)
    
    def __get_unique_codevalue(self):
        code = self.codename
        return getattr(self, code)
    codevalue = property(fget = __get_unique_codevalue)
        
    def get_admin(self):
        return get_admin(self)
    
    def save_and_log(self, user, msg='', flag = None):
        return _save_and_log(self, user, msg, flag)
        
    def delete_and_log(self,user,msg=''):
        return _delete_and_log(self,user,msg)
    
    class Meta:
        abstract = True