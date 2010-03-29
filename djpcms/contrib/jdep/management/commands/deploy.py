import os
import re
from optparse import make_option

from django.template import loader
from django.contrib.sites.models import Site
from django.contrib.contenttypes.management import update_all_contenttypes
from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module
from django.contrib.auth import authenticate
 
from djpcms.contrib.jdep import settings
from djpcms.contrib.compressor.storage import application_map
from djpcms.contrib.jdep.models import DeploySite
from djpcms.contrib.jdep.utils import prompt
 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--port', dest='port', default=80,
            help='Specifies the nginx port.'),
        make_option('--apache_port', dest='apache_port', default=95,
            help='Specifies the apache_port to redirect.'),
        make_option('--servername', dest='servername', default=None,
            help='Specifies the nginx servername.'),
        make_option('--server_user', dest='server_user', default=None,
            help='Specifies the apache and nginx user.'),
        make_option('--server_group', dest='server_group', default=None,
            help='Specifies the apache and nginx group.'),
        make_option('--python_path', dest='python_path', default=None,
            help='Specifies the python path.'),
            )
    help = "Clean prospero instruments"
 
    def handle(self, *args, **options):
        cwd = os.getcwd()
        base = os.path.split(cwd)[0]
        servername = options.get('servername',None)
        if servername is None:
            site = Site.objects.get_current()
            servername = site.domain
        map = application_map()
        server_user = options.get('server_user',None)
        server_group = options.get('server_group',server_user)
        
        username = prompt('username: ')
        password = prompt('password: ')
        comment  = prompt('comment: ')
        user = authenticate(username = username, password = password)
        if user is not None and user.is_active:
            dep = DeploySite(user = user, comment = comment)
            dep.save()
        else:
            print("Not authorised")
            exit(1)
        
        depid = dep.getval()
        
        if os.name == 'posix':
            logname = 'log/prospero_%s.log' % depid
        else:
            logname = 'log\\prospero_%s.log' % depid
            
        context = {'path': cwd,
                   'base_path': base,
                   'apps': map.values(),
                   'server_name': servername,
                   'port': options.get('port', 80),
                   'apache_port': options.get('apache_port',95),
                   'nginx_access': logname,
                   'media': os.path.join(cwd,'media','site'),
                   'server_user': server_user,
                   'server_group': server_group,
                   'project_name': '%s_%s' % (settings.PROJECT_NAME,depid),
                   'threads': settings.SERVER_THREADS}
        # Nginx
        data = loader.render_to_string('jdep/nginx.conf', context)
        f = open(os.path.join(base,'prospero_nginx_%s.conf' % depid),'w')
        f.write(data)
        context.pop('server_name',None)
        
        # Apache
        data = loader.render_to_string('jdep/mod_wsgi.conf', context)
        f = open(os.path.join(base,'prospero_apache_%s.conf' % depid),'w')
        f.write(data)
        
        f.close()

