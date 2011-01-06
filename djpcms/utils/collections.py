import sys
from collections import *

if sys.version_info < (2,7):
    from djpcms.utils.fallbacks._collections import *