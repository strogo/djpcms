import os
import sys

VERSION = (0, 5, 'alpha')

def get_version():
    if len(VERSION) == 3:
        v = '%s.%s_%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v

siteapp_choices = [('','-----------------')]
        

__version__ = get_version()
