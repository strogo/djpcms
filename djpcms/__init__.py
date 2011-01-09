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
        module = __import__(module_name)
        libs.append(module)
    
    
def install_libs():
    if path_dir not in sys.path:
        sys.path.insert(0,path_dir)
    libs = os.path.join(this_dir,'libs')
    install_lib(libs, 'django-tagging', 'tagging')
    install_lib(libs, 'djpadmin', 'djpadmin')
    #install_lib(libs, 'BeautifulSoup', 'BeautifulSoup')
    
    
def init_logging(clear_all = False):
    '''Initialise logging'''
    from djpcms.utils.log import dictConfig
    
    if clear_all:
        import logging
        logging.Logger.manager.loggerDict.clear()

    if sites.settings.LOGGING:
        dictConfig(sites.settings.LOGGING)
        
    
install_libs()

