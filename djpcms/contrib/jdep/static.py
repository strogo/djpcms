import os
from django.template import loader
from django.utils._os import safe_join

from djpcms.utils.importlib import import_module

    
class pathHandler(object):
    
    def __init__(self, mediaprefix, name, path):
        self.mediaprefix = mediaprefix
        self.name        = name
        self.base        = path
        self._path       = os.path.join(path,'media')
        self.fullpath    = self.path(name)
        self.exists      = os.path.exists(self._path)
    
    def path(self, name):
        return safe_join(self._path, name)
    
    def url(self):
        return '%s%s/' % (self.mediaprefix,self.name)
        
    def __str__(self):
        return self.name


class djangoAdminHandler(pathHandler):
    
    def path(self, name):
        name = (name.split('/')[1:])
        return safe_join(self._path, *name)


def application_map():
    map = {}
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        sapp = app.split('.')
        name = sapp[-1]
        if app.startswith('django.'):
            if app == 'django.contrib.admin':
                base = settings.ADMIN_MEDIA_PREFIX[1:-1].split('/')[-1]
                handler = djangoAdminHandler
            else:
                continue
        else:
            base    = name
            handler = pathHandler
            
        try:
            module = import_module(app)
        except:
            continue

        path   = module.__path__[0]
        map[base] = handler(settings.MEDIA_URL,name,path)
    return map


def config_file(fname, ext = 'conf', environ=None, dir = None):
    '''Create a configuration file from template and return the filename

* fname: one of nginx, mod_wsgi, mod_python, django
* ext: conf or wsgi
* dir: directory containing the file or None. If none no file will be saved.
    '''
    filename = '%s.%s' % (fname,ext)
    template = os.path.join('jdep',filename)
    data = loader.render_to_string(template,environ)
    if dir:
        filename = '%s_%s' % (environ['project'],filename)
        fullpath = os.path.join(dir,filename)
        f = open(fullpath,'w')
        f.write(data)
        f.close()
        return filename
    else:
        return data
    
    
class ServerInstaller(object):
    
    def config(self, release = True):
        from fabric.api import env, run
        if release:
            run('python ./server.py')
            run('rm server.py')
        else:
            exec(env.server_script)

    def reboot(self):
        pass


class nginx_apache_wsgi(ServerInstaller):

    def __str__(self):
        return 'nginx + apache (mod_wsgi)'
    
    def config_files(self, environ, release = True):
        environ['apps']  = application_map().values()
        dir = None if not release else environ['confdir']
        wsgi = None if not release else environ['release_path']
        environ['nginx'] = config_file('nginx',environ=environ,dir=dir)
        environ['wsgi'] = config_file('django','wsgi',environ=environ,dir=wsgi)
        environ['apache'] = config_file('mod_wsgi',environ=environ,dir=dir)
        if not release:
            from __builtin__ import globals
            g = globals()
            g['script_result'] = environ
        
    def install(self, release = True):
        from fabric.api import env, sudo
        self.config(release)
        if release:
            sudo('cp %(confdir)s/%(apache)s /etc/apache2/sites-available/' % env)
            try:
                sudo('rm /etc/apache2/sites-enabled/%(apache)s' % env)
            except:
                pass
            sudo('ln -s /etc/apache2/sites-available/%(apache)s /etc/apache2/sites-enabled/%(apache)s' % env)
            
            sudo('cp %(confdir)s/%(nginx)s /etc/nginx/sites-available/' % env)
            try:
                sudo('rm /etc/nginx/sites-enabled/%(nginx)s' % env)
            except:
                pass
            sudo('ln -s /etc/nginx/sites-available/%(nginx)s /etc/nginx/sites-enabled/%(nginx)s' % env)
            if env.get('server_user',None):
                sudo('chown %(server_user)s:%(server_group)s -R %(logdir)s' % env)
        else:
            self.result = script_result
        return self

    def reboot(self):
        from fabric.api import sudo
        sudo("/etc/init.d/nginx restart")
        sudo('/etc/init.d/apache2 restart')
        return self

    def info(self):
        from fabric.api import env
        print('apache port:        %(apache_port)s' % env)
        
        
        
server_types = {'nginx-apache-mod_wsgi':nginx_apache_wsgi(),
                }
