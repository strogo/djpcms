#
# Load the markup module
# This hook is provided so that third-party murkup libraries
# to process murkup languages can be used rather than the limited one
# in djpcms
from djpcms.settings import DJPCMS_MARKUP_MODULE

markup_module = __import__(DJPCMS_MARKUP_MODULE,globals(),locals(),[''])

#
# The murkup module must provide the following 3 methods


# list of 2-elements tuples to use in Report model markup choice
choices = markup_module.choices

# default markup, a string
default = markup_module.default

# get method to obtain the markup handler
get = markup_module.get
