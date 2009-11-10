from django.db import models
from django.utils.encoding import force_unicode, smart_str
from django.utils.text import capfirst
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from pmodel import *

__all__ = ['TimeStamp','puser','Tag','TagLower','CodeDescriptionModel']
    
    
class TimeStamp(models.Model):
    last_modified     = models.DateTimeField(auto_now = True)
    created           = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True
        
        
class puser(Pmodel):
    user = models.ForeignKey(User, unique=True, verbose_name = 'username')
    
    def has_perm(self, perm):
        return self.user.has_perm(perm)
    
    class Meta:
        abstract = True
        
        
class Tag(Pmodel):
    code = models.CharField(unique = True, max_length=32)
    name = models.CharField(max_length=62, blank = True)
    
    def __unicode__(self):
        return u'%s' % self.code
    
    class Meta:
        abstract = True


class CodeDescriptionModel(Tag):
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        n = self.name
        if n:
            return u'%s - %s' % (self.code,n)
        else:
            return u'%s' % self.code
        
    class Meta:
        abstract = True

        
class TagLower(Tag):
    
    def save(self):
        c = self.code.lower()
        self.code = c
        super(TagLower,self).save()
        
    class Meta:
        abstract = True
        
    
class ApplicationBase(Pmodel):
    '''
    Base class for web-application models
    '''
    path               = 'prospero.contrib.analytics.modules'
    code               = models.CharField(max_length=12, unique = True, help_text="The unique application code")
    title              = models.CharField(max_length=20)
    long_title         = models.CharField(max_length=40)
    description        = models.CharField(max_length=500)
    
    def relative_path(self, delim = '.'):
        from string import lower
        return lower('%s' % self.code)
        
    def __unicode__(self):
        return u'%s' % self.relative_path('.')
    
    def get_view(self, master):
        m = self.get_module()
        url = master.url() % self.code
        return m.model(self, title = self.title, master = master, url = url)
    
    def get_module(self):
        from qmpy.python.runtime import get_mod
        pa = self.path
        if pa:
            dot_path   = '%s.%s' % (self.path,self.relative_path())
        else:
            dot_path   = self.relative_path()
        try:
            return get_mod(dot_path)
        except:
            return None

    class Meta:
        abstract = True


def jtable_from_model(obj, post_params = None, NoneType = None):
    if hasattr(obj,'jtable'):
        return obj.jtable(post_params,NoneType)
    else:
        return _jtable_from_model(obj, post_params,NoneType)
    
def save_and_log(obj, user, msg = '', flag = None):
    if hasattr(obj,'save_and_log'):
        return obj.save_and_log(user, msg, flag)
    else:
        return __save_and_log(obj, user, msg, flag)
    
def delete_and_log(obj,user,msg=''):
    if hasattr(obj,'delete_and_log'):
        return obj.delete_and_log(user,msg)
    else:
        return __delete_and_log(obj,user,msg)
    
    

     
def _jtable_from_model(obj, post_params = None, NoneType = None):
    '''
    Return a JSON table representing object model obj
    '''
    from user import User, Group, UserHandle, GroupHandle, add_field_to_table
    from qmpy.django.views.table import jtable
    t = jtable(post_params=post_params)
    t.appendfield(('','string'),False)
    t.appendfield(('Value','string'),False)
    if obj.__class__ == User:
        return UserHandle(obj).jtable(t,NoneType)
    elif  obj.__class__ == Group:
        return GroupHandle(obj).jtable(t,NoneType)
    return add_field_to_table(obj,t,NoneType)

