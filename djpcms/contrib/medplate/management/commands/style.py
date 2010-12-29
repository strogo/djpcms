import os
from optparse import make_option

from djpcms.conf import settings
from djpcms import template
from djpcms.utils.importlib import import_module
from djpcms.apps.management.base import BaseCommand


default_style = 'allwhite'


def render(style, target, template_engine = None):
    module = None
    
    if not style:
        #try style file in project directory
        modname = '{0}.style'.format(settings.SITE_MODULE)
        try:
            module = import_module(modname)
        except ImportError:
            pass
    
    if not module:
        style = style or default_style
        bits = style.split('.')
        if len(bits) == 1:
            modname = 'djpcms.themes.{0}'.format(style)
        else:
            raise ValueError('Style {0} not available'.format(style))
        try:
            module = import_module(modname)
        except ImportError:
            raise ValueError('Style {0} not available'.format(style))
    
    context = module.context.copy()
    context.update({'MEDIA_URL': settings.MEDIA_URL})
    data = context.render(template_engine)
    f = open(target,'w')
    f.write(data)
    f.close()



class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s','--style',
                     action='store',
                     dest='style',
                     default='',
                     help='Style to use.'),
        make_option('-t','--target',
                    action='store',
                    dest='target',
                    default='media/site/site.css',
                    help='Target path of css file.'),
    )
    help = "Creates a css file from a template css."
    
    def handle(self, *args, **options):
        style = options['style']
        target = os.path.join(settings.SITE_DIRECTORY,options['target'])
        render(style,target)
        
        
        