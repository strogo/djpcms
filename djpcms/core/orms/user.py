'''Monkey patch wrapper for User ORM
'''

def monkey_patch_user(wrapper):
    if wrapper.orm == 'django':
        from django.contrib.auth import authenticate, login, logout
        wrapper.authenticate = authenticate
        wrapper.login = login
        wrapper.logout = logout
    elif wrapper.orm == 'stdnet':
        model = wrapper.model
        wrapper.authenticate = model.authenticate
        wrapper.login = model.login
        wrapper.logout = model.logout
    return wrapper
