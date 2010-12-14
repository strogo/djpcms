import os
import sys
from flowrepo import settings

if settings.LATEX_PYTHON_PATH not in sys.path:
    sys.path.insert(0,settings.LATEX_PYTHON_PATH)
    
os.environ['TEXINPUTS'] = '%s:.::' % settings.LATEX_TEMPLATE_PATH
os.environ['XHTMLTEMPLATES'] = settings.LATEX_TEX_PATH