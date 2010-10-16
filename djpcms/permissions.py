'''Permission for inline editing'''
from django.contrib.auth.backends import ModelBackend

from djpcms.conf import settings
from djpcms.utils import function_module



def get_view_permission(obj):
    return '%s_view' % obj._meta


def has_permission(user, permission_codename, obj=None):
    from djpcms.models import Page, BlockContent
    if not obj:
        return user.has_perm(permission_codename)
    else:
        anony = user.is_anonymous()
        opts = obj._meta
        
        viewperm     = get_view_permission(obj) == permission_codename
        changeperm   = opts.get_change_permission() == permission_codename
        
        # Do Page and BlockContent first
        if isinstance(obj,Page):
            if anony and obj.requires_login:
                return False
            if changeperm and obj.user == user and settings.DJPCMS_USER_CAN_EDIT_PAGES:
                return True
        elif isinstance(obj,BlockContent):
            if changeperm and obj.page.user == user and settings.DJPCMS_USER_CAN_EDIT_PAGES:
                return True
            if viewperm and not anony and obj.for_not_authenticated:
                return False
        
        return viewperm or sup_has_perm(user, permission_codename)
        

def _inline_editing(request, page, obj = None):
    '''
    Default function for editing permissions
    '''
    user = request.user
    if user.is_authenticated():
        if user.is_superuser or user == page.user:
            return True            
        elif user.groups.filter(name = 'editor') and not page.user:
            return True
        else:
            return False
    else:
        return False
    

def inline_editing(request, page, obj = None):
    from djpcms.conf import settings
    editing = settings.CONTENT_INLINE_EDITING
    if editing.get('available',False):
        func = function_module(editing.get('permission',None),_inline_editing)
        try:
            if func(request, page, obj):
                return '/%s%s' % (editing.get('preurl','edit'),request.path)
            else:
                return False
        except:
            return False
    else:
        return False
    
    
class Backend(ModelBackend):
    '''Permission backend which complement the standard django backend.'''
    supports_object_permissions = True
    supports_anonymous_user = True

    def has_perm(self, user, permission_codename, obj=None):
        sup_has_perm = super(Backend,self).has_perm
        return sup_has_perm(user, permission_codename)