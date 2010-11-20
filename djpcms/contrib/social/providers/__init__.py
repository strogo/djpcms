def safeimport(name):
    try:
        __import__(name)
    except ImportError:
        pass

safeimport('twitter')
safeimport('google')