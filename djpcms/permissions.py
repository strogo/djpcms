'''Permission for inline editing'''
from django.contrib.auth.backends import ModelBackend

from djpcms.conf import settings
from djpcms.utils import function_module



def get_view_permission(obj):
    return '%s_view' % obj._meta

def get_change_permission(obj):
    opts = obj._meta
    return opts.app_label + '.' + opts.get_change_permission()


def has_permission(user, permission_codename, obj=None):
    from djpcms.models import Page, BlockContent, ObjectPermission
    if not obj:
        back = ModelBackend()
        if permission_codename[-4:] == 'view':
            return True
        if not user.is_active:
            return False
        if user.is_superuser:
            return True
        return back.has_perm(user, permission_codename)
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
            if anony and obj.requires_login:
                return False
            if changeperm and obj.page.user == user and settings.DJPCMS_USER_CAN_EDIT_PAGES:
                return True
            if viewperm and not anony and obj.for_not_authenticated:
                return False
        
        if user.is_superuser:
            return True
        
        perms = ObjectPermission.objects.for_object(obj, permission_codename)
        if perms:
            for perm in perms:
                if perm.has_perm(user):
                    return True
        
        # Fall back to permission without object
        return has_permission(user, permission_codename)
    

def inline_editing(request, page, obj = None):
    from djpcms.conf import settings
    editing = settings.CONTENT_INLINE_EDITING
    if editing.get('available',False):
        if has_permission(request.user, get_change_permission(page), page):
            return '/%s%s' % (editing.get('preurl','edit'),request.path)
    return False
    
    
class Backend(ModelBackend):
    '''Permission backend which complement the standard django backend.'''
    supports_object_permissions = True
    supports_anonymous_user = True

    def has_perm(self, user, permission_codename, obj=None):
        return has_permission(user, permission_codename, obj)
        