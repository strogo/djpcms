
def get_http(lib):
    mod = None
    if lib == 'django':
        from djpcms.http import _django as mod
    elif lib == 'werkzeug':
        from djpcms.http import _werkzeug as mod
    return mod


def make_wsgi(site):
    mod = None
    if site.settings.HTTP_LIBRARY == 'django':
        from djpcms.http import _django as mod
    elif site.settings.HTTP_LIBRARY == 'werkzeug':
        from djpcms.http import _werkzeug as mod
    return mod.make_wsgi(site)
        
    