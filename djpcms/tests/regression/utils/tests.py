import sys

from .strings import *

if sys.version_info < (2,7):
    from ordereddict import *