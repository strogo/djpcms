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
    
    def url(self):
        return self.mediaprefix


def application_map():
    map = {}
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        sapp = app.split('.')
        name = sapp[-1]
        if app.startswith('django.'):
            if app == 'django.contrib.admin':
                base = 'admin'
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


def config_file_name(fname, environ):
    return '%s_%s' % (environ['project'],fname)


def config_file(fname, environ=None, dir = None):
    '''Create a configuration file from template and return the filename

* *fname*: The template used to create the file
* *dir*: directory containing the file or None. If none no file will be saved.
    '''
    template = os.path.join('jdep',fname)
    data = loader.render_to_string(template,environ)
    if dir:
        filename = config_file_name(fname, environ)
        fullpath = os.path.join(dir,filename)
        f = open(fullpath,'w')
        f.write(data)
        f.close()
        return filename
    else:
        return data
    
    

def vrun(command = ''):
    '''Run a command in the server virtual environment.'''
    from fabric.api import env, run
    elem = 'cd %(release_path)s; source bin/activate' % env
    if command:
        elem = '%s; %s' % (elem,command)
    run(elem)
    
    
    
class ServerInstaller(object):
    
    def config(self, release = True):
        if release:
            vrun('python server.py')
        else:
            # very problematic to debug this statement. Need a better way.
            exec(self.env.server_script)
    
    def config_files(self, environ, release = True):
        pass
    
    def __get_env(self):
        from fabric.api import env
        return env
    env = property(__get_env)

    def info(self, data):
        pass
    
    def install(self, release = True):
        return self
    
    def reboot(self):
        pass
    

class NginxBase(ServerInstaller):
    
    def config_files(self, environ, release = True):
        rs = [environ.domain_name] + environ.redirects
        v  = []
        for r in rs:
            v.append(r.replace('.','\.'))
        environ.nginx_redirects = '|'.join(v)


class nginx_apache_wsgi(ServerInstaller):
    '''Nginx + Apache mod_wsgi server'''
    nginx  = 'nginx.conf'
    apache = 'apache_mod_wsgi.conf'
    django = 'django.wsgi'
     
    def __str__(self):
        return 'nginx + apache (mod_wsgi)'
    
    def config_files(self, environ, release = True):
        super(nginx_apache_wsgi,self).config_files(environ,release)
        # Create the config files. Function called from remote server
        environ['apps']  = application_map().values()
        dir = None if not release else environ['confdir']
        wsgi = None if not release else environ['release_path']
        environ['nginx']  = config_file(self.nginx,environ=environ,dir=dir)
        environ['wsgi']   = config_file(self.django,environ=environ,dir=wsgi)
        environ['apache'] = config_file(self.apache,environ=environ,dir=dir)
        if not release:
            from __builtin__ import globals
            g = globals()
            g['script_result'] = environ
        
    def install(self, release = True):
        from fabric.api import env, sudo
        self.config(release)
        if release:
            env.apache = config_file_name(self.apache,env)
            env.nginx  = config_file_name(self.nginx,env)
            
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

    def info(self, data):
        data['apache port'] = self.env['redirect_port']
        


class nginx_twisted(NginxBase):
    '''Twisted behind nginx server'''
    nginx  = 'nginx.conf'
    
    def __str__(self):
        return 'Twisted behind nginx'
    
    def info(self, data):
        data['twisted port'] = self.env['redirect_port']
        
    def config_files(self, environ, dir = None, release = True):
        super(nginx_twisted,self).config_files(environ,release)
        # Create the config files. Function called from remote server
        environ['apps']  = application_map().values()
        if dir is None:
            dir = None if not release else environ['confdir']
        environ['nginx']  = config_file(self.nginx,environ=environ,dir=dir)
        if not release:
            from __builtin__ import globals
            g = globals()
            g['script_result'] = environ
    
    
        
        
server_types = {'nginx-apache-mod_wsgi':nginx_apache_wsgi(),
                'nginx-twisted':nginx_twisted()}
