import os
import sys

VERSION = (0, 4, 'beta')

def get_version():
    if VERSION[2] is not None:
        v = '%s.%s_%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v


def install():
    pp = os.path.join(os.path.dirname(__file__),'plugins')
    if pp not in sys.path:
        sys.path.insert(0, pp)


install()
__version__ = get_version()