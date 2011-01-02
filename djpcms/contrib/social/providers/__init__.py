

def safeimport(name):
    try:
        __import__('djpcms.contrib.social.providers.{0}'.format(name))
    except ImportError, e:
        pass

safeimport('flickr')
safeimport('google')
safeimport('twitter')
safeimport('yahoo')