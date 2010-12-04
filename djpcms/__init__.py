'''Dynamic content management system using Javascript and Python'''

VERSION = (0, 8, '6dev')


def get_version():
    if len(VERSION) == 3:
        v = '%s.%s.%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v

# This list is updated by the views.appsite.appsite handler
siteapp_choices = [('','-----------------')]


__version__  = get_version()
__license__  = "BSD"
__author__   = "Luca Sbardella"
__contact__  = "luca.sbardella@gmail.com"
__homepage__ = "http://djpcms.com/"


import os
import sys
from apps import MakeSite, get_url

parent = lambda x : os.path.split(x)[0]
this_dir = parent(os.path.abspath(__file__))
libs = []


def get_site():
    from djpcms.views.appsite import site
    return site


def runtests(tags = None, verbosity = 1, interactive = True, failfast = False):
    '''Run tests::
    
    import djpcms
    djpcms.runtests()'''
    path_dir = parent(this_dir)
    if path_dir not in sys.path:
        sys.path.insert(0,path_dir)
    from djpcms.tests.runtests import run
    run(tags, verbosity, interactive, failfast)


def install_lib(basepath, dirname, module_name):
    try:
        __import__(module_name)
    except ImportError:
        dir = os.path.join(basepath,dirname)
        sys.path.insert(0,dir)
        module = __import__(module_name)
        libs.append(module)
    
    
def install_libs():
    libs = os.path.join(this_dir,'libs')
    install_lib(libs, 'django-tagging', 'tagging')
    
    
def init_logging(clear_all = False):
    '''Initialise logging'''
    from djpcms.utils.log import dictConfig
    from djpcms.conf import settings
    
    if clear_all:
        import logging
        logging.Logger.manager.loggerDict.clear()

    if settings.LOGGING:
        dictConfig(settings.LOGGING)
        
    
install_libs()

