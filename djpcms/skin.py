
__all__ = ['set_skin_style','get_skin_style']

def _get_skin_style_default(view):
    from django.conf import settings
    s = 'djpcms/css/skins/smooth/base.css'
    return '%s%s' % (settings.MEDIA_URL,s)


skin_style_function_holder = [_get_skin_style_default]


def set_skin_style(fun):
    global skin_style_function_holder
    skin_style_function_holder[0] = fun
    
def get_skin_style(view):
    global skin_style_function_holder
    fun = skin_style_function_holder[0]
    return fun(view) 