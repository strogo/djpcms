import os

# Target machine settings and configuration
defaults = {'server_type':        'mod_wsgi',   #mod_wsgi or None for now
            'server_user':        'www-data',
            'server_group':       'www-data',
            'server_name':        None,
            'threads':            15,
            'apache_port':        90,
            'python_version':     '2.6',
            'path':               None,
            'project_name':       None,
            'no_site_packages':   False,
            'server_admin':       None}


def project(module, deploy_root_dir = 'deployment', setting_name = None):
    '''Setup django project for deployment using fabric.

* *module* is the name of the module containing the site. It must be on the same directory as the fabfile used to upload.
* *setting_name* optional settings file name (default is "settings").
* *deploy_root_dir* optional root directory where file will be installed (Default is "deployment").'''
    from fabric.api import env
    env.project = module
    env.path = os.path.join(deploy_root_dir,module)
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.%s' % (module,setting_name or 'settings')
    

def sitearchive():
    

def prompt(text, default=''):
    default_str = ''
    if default != '':
        default_str = ' [%s] ' % str(default).strip()
    else:
        default_str = ' '
    prompt_str = text.strip() + default_str
    return raw_input(prompt_str) or default


def create_deploy():
    from django.template import loader
    from django.contrib.auth import authenticate
    from models import DeploySite
    user = authenticate(username = username, password = password)
    if user is not None and user.is_active:
        dep = DeploySite(user = user, comment = comment)
        dep.save()
    else:
        exit(1)