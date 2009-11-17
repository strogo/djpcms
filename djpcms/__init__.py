import os
import sys

VERSION = (0, 4, 'beta')

def get_version():
    if VERSION[2] is not None:
        v = '%s.%s_%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v

siteapp_choices = []
        

__version__ = get_version()
