
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


def serve(site, using = None, **kwargs):
    '''Serve DJPCMS applications'''
    if not using:
        using = site.settings.HTTP_LIBRARY
    if using == 'django':
        from djpcms.http import _django as mod
    elif using == 'werkzeug':
        from djpcms.http import _werkzeug as mod
    else:
        raise ValueError('Cannot serve with {0}. Not available.'.format(using))
    mod.serve(**kwargs)
    
        
    