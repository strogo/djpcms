from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module
import os
import re
from random import choice

djpcms_defaults = '''# djpcms settings
DEFAULT_TEMPLATE_NAME = 'base.html'
CONTENT_INLINE_EDITING = {'available':      True,
                          'pagecontent':    '/site-content/',
                          'width':          600,
                          'height':         500}
'''


class Command(BaseCommand):
    help = "Adapt a new Django project directory structure to djpcms."
    args = "[projectname]"
    label = 'project name'

    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        # Determine the project_name a bit naively -- by looking at the name of
        # the parent directory.
        directory = os.getcwd()
        setting_module = os.environ['DJANGO_SETTINGS_MODULE']
        setting_filename = setting_module.split('.')[1] 
        main_settings_file = os.path.join(directory, '%s.py' % setting_filename)
        
        # Read the setting file
        settings_contents = open(main_settings_file, 'r').read()
        
        # Open the setting file for writing
        fp = open(main_settings_file, 'w')
        #settings_contents = re.sub(r"(?<=SECRET_KEY = ')'", secret_key + "'", settings_contents)
        settings_contents = '%s\n\n%s' % (settings_contents,djpcms_defaults)
        fp.write(settings_contents)
        fp.close()
    