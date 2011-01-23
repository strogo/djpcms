'''Dynamic content management system using Javascript and Python'''

VERSION = (0, 9, 'dev')

def get_version():
    return '.'.join(map(str,VERSION))

# This list is updated by the views.appsite.appsite handler
siteapp_choices = [('','-----------------')]


__version__   = get_version()
__license__   = "BSD"
__author__    = "Luca Sbardella"
__contact__   = "luca.sbardella@gmail.com"
__homepage__  = "http://djpcms.com/"
__docformat__ = "restructuredtext"


import os
import sys
from .apps import *
from .http import serve

parent = lambda x : os.path.split(x)[0]
this_dir = parent(os.path.abspath(__file__))
path_dir = parent(this_dir)
libs = []

def install_lib(basepath, dirname, module_name):
    try:
        __import__(module_name)
    except ImportError:
        dir = os.path.join(basepath,dirname)
        sys.path.insert(0,dir)
        try:
            module = __import__(module_name)
            libs.append(module)
        except ImportError:
            pass
    
    
def install_libs():
    if path_dir not in sys.path:
        sys.path.insert(0,path_dir)
    dlibs = os.path.join(this_dir,'libs')
    install_lib(dlibs, 'django-tagging', 'tagging')
    install_lib(dlibs, 'djpadmin', 'djpadmin')
    install_lib(dlibs, 'BeautifulSoup', 'BeautifulSoup')
    
    
def init_logging(clear_all = False):
    '''Initialise logging'''
    from djpcms.utils.log import dictConfig
    
    if clear_all:
        import logging
        logging.Logger.manager.loggerDict.clear()

    settings = sites.settings
    if settings:
        if settings.DEBUG:
            settings.LOGGING['root'] = {
                                        'handlers': ['console'],
                                        'level': 'DEBUG',
                                        }
        dictConfig(settings.LOGGING)
        
    
install_libs()

