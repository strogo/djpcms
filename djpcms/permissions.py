'''
Default permission for inline editing
'''

from djpcms.utils import function_module

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