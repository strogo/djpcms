from django.utils.text import capfirst
from django.contrib.auth.models import User, AnonymousUser , Group
from field import _boolean_icon, field_repr, datetime_repr, field_value
from base import *

__all__ = ['authenticate',
           'get_user',
           'add_field_to_table',
           'User']
    
def authenticate(username, password):
    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)
    return get_user(user)

def get_user(user):
    if not isinstance(user,User):
        try:
            user = User.objects.get(username = str(user))
        except:
            user = AnonymousUser()
            
    if not isinstance(user,User):
        user = AnonymousUser()
        user.preference = None
    
    else:
        try:
            user.preference = user.get_profile()
            return user.preference
        except:
            user.preference = None
            return user


def add_field_to_table(obj,t,NoneType=None):
    '''
    Add fields in admin.list_display to a jason table.
    obj must be an instance of qmpy.django.models.abstract.pmodel
    '''
    if obj == None:
        return t
    try:
        admin = obj.get_admin()
    except:
        admin = get_admin(obj)
        
    if admin:
        list_display = admin.list_display
        for field_name in list_display:
            fname, field_val = field_value(obj,field_name,NoneType)
            t.appenddatarow([capfirst(fname),field_val])
        return t
    else:
        return t

class UserHandle(object):
    
    def __init__(self,user):
        self.user = get_user(user)
        
    def jtable(self,t,NoneType=None):
        u = self.user
        t = add_field_to_table(u.preference,t,NoneType)
        if u.preference == None:
            t.appenddatarow(['Username',u.username])
        t.appenddatarow(['Name',u.get_full_name()])
        t.appenddatarow(['Active',_boolean_icon(u.is_active)])
        t.appenddatarow(['Superuser',_boolean_icon(u.is_superuser)])
        t.appenddatarow(['Last login',datetime_repr(u.last_login)])
        t.appenddatarow(['Joined Date',datetime_repr(u.date_joined)])
        return t
        
        
    
    
class GroupHandle(object):
    
    def __init__(self,user):
        self.user = user
        self.prof = user.get_profile()
        
    def jtable(self,t,NoneType=None):
        return t