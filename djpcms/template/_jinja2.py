from djpcms.conf import settings
from jinja2 import Environment, PackageLoader, Template


env = Environment(loader=PackageLoader('yourapplication', 'templates'))
