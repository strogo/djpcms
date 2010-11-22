def safeimport(name):
    try:
        __import__(name)
    except ImportError:
        pass

safeimport('flickr')
safeimport('google')
safeimport('twitter')