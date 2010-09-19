import os

from django.template import loader
from django.utils._os import safe_join

from fabric.api import env, run, put, local, sudo

from djpcms.utils.importlib import import_module


# Target machine settings and configuration
defaults = {'server_type':        'nginx-apache-mod_wsgi',
            'server_user':        'www-data',
            'server_group':       'www-data',
            'server_name':        None,
            'threads':            15,
            'apache_port':        90,
            'python_version':     '2.6',
            'path':               None,
            'project_name':       None,
            'with_site_packages': False,
            'server_admin':       None}


def project(module, domain_name, deploy_root_dir = 'deployment', setting_name = None, **kwargs):
    '''Setup django project for deployment using fabric.

* *module* is the name of the module containing the site. It must be on the same directory as the fabfile used to upload.
* *domain_name* the site domain name (for configuring web servers).
* *setting_name* optional settings file name (default is "settings").
* *deploy_root_dir* optional root directory where file will be installed (Default is "deployment").'''
    env.project = module
    env.domain_name = domain_name
    env.path = os.path.join(deploy_root_dir,module)
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.%s' % (module,setting_name or 'settings')
    env.update(kwargs)
    

def makedir(path):
    '''Safely create a directory in the server'''
    tomake = []
    notdone = True
    while notdone:
        try:
            run('mkdir %s' % path)
            notdone = False
        except SystemExit:
            path,next = os.path.split(path)
            tomake.append(next)
    for dir in reversed(tomake):
        path = os.path.join(path,dir)
        run('mkdir %s' % path)
            
    
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
        
        
def rmgeneric(path, __func__):
    try:
        __func__(path)
        #print 'Removed ', path
        return 1
    except OSError, (errno, strerror):
        print 'Could not remove %s, %s' % (path,strerror)
        return 0
        
 
def rmfiles(path, ext = None):    
    if not os.path.isdir(path):
        return 0
    trem = 0
    tall = 0
    files = os.listdir(path)
    for f in files:
        fullpath = os.path.join(path, f)
        if os.path.isfile(fullpath):
            sf = f.split('.')
            if len(sf) == 2:
                if ext == None or sf[1] == ext:
                    tall += 1
                    trem += rmgeneric(fullpath, os.remove)
        elif os.path.isdir(fullpath):
            r,ra = rmfiles(fullpath, ext)
            trem += r
            tall += ra
    return trem, tall



def config_file(fname, ext = 'conf', dir = None):
    '''Create a configuration file from template and return the filename

* fname: one of nginx, mod_wsgi, mod_python, django
* ext: conf or wsgi
* dir: directory containing the file or None. If none no file will be saved.
    '''
    filename = '%s.%s' % (fname,ext)
    template = os.path.join('jdep',filename)
    data = loader.render_to_string(template,env)
    if dir:
        data = open('{2}/{0}.{1}'.format(fname,ext,dir),'r').read()
        ngdata = data.format(env)
        f = open(filename,'w')
        f.write(ngdata)
        f.close()
        return filename
    else:
        return data


def startvirtualenv():
    run('cd %(release_path)s; source bin/activate' % env)
    
    
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
    #settings = import_module(os.environ['DJANGO_SETTINGS_MODULE'])
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

    
    
def install_site(release = True):
    env.logdir = '%(release_path)s/logs' % env
    env.confdir = '%(release_path)s/conf' % env
    env.apps = application_map().values()
    if release:
        run('cd; mkdir %(logdir)s; mkdir %(confdir)s' % env)
    server = server_types[env.server_type]
    return server.install(release)


class ServerInstaller(object):
    pass


class nginx_apache_wsgi(ServerInstaller):

    def __str__(self):
        return 'nginx + apache (mod_wsgi)'
    
    def install(self, release = True):
        env.nginx_assess_log = '%(logdir)s/nginx_access.log' % env
        dir = None if not release else os.getcwd()
        result = {}
        result['nginx']  = config_file('nginx',dir=dir)
        result['apache'] = config_file('mod_wsgi',dir=dir)
        result['wsgi']   = config_file('django','wsgi',dir=dir)
        
        if release:
            for k,v in result.items():
                put(v, env.confdir)
                local('rm %s' % k)
        
            sudo('cp {0}/{1} /etc/apache2/sites-available/'.format(release,apache))
            try:
                sudo('rm /etc/apache2/sites-enabled/{0}'.format(apache))
            except:
                pass
            sudo('ln -s /etc/apache2/sites-available/{0} /etc/apache2/sites-enabled/{0}'.format(apache))
            
            sudo('cp {0}/{1} /etc/nginx/sites-available/'.format(release,nginx))
            try:
                sudo('rm /etc/nginx/sites-enabled/{0}'.format(nginx))
            except:
                pass
            sudo('ln -s /etc/nginx/sites-available/{0} /etc/nginx/sites-enabled/{0}'.format(nginx))
            if env.get('server_user',None):
                sudo('chown {0[server_user]}:{0[server_group]} -R {0[logdir]}'.format(target))
        return result

    def reboot(self):
        sudo("/etc/init.d/nginx restart")
        sudo('/etc/init.d/apache2 restart')

    def info(self):
        print('apache port:        %(apache_port)s' % env)



server_types = {'nginx-apache-mod_wsgi':nginx_apache_wsgi(),
                }






def python_version():
    '''Python version'''
    run('python --version')


def python_path():
    env.python_path = '{0[path]}/lib/python{0[version]}/site-packages'.format(env)


def git_pull():
    "Updates the repository."
    run("cd ~/git/$(repo)/; git pull $(parent) $(branch)")


def git_reset():
    "Resets the repository to specified version."
    run("cd ~/git/$(repo)/; git reset --hard $(hash)")
    
def symlink(origin, target):
    run('ln -s {0} {1}')
    

def upload_tar_from_git():
    "Create an archive from the current Git master branch and upload it"
    local('git archive --format=tar master | gzip > release.tar.gz' % env)
    run('mkdir %(path)s/releases/%(release)s' % env)
    
    # put tar package
    put('release.tar.gz', '%(path)s' % env)
    
    run('cd %(path)s/releases/%(release)s && tar zxf ../../release.tar.gz' % env)
    run('rm %(path)s/release.tar.gz' % env)
    
    # Put the machines file
    put('%(module_name)s/machines.py' % env, '%(path)s/releases/%(release)s/%(module_name)s' % env)
    
    local('rm release.tar.gz')


def symlink_current_release():
    "Symlink our current release"
    run('cd %(path)s/releases; rm previous; mv current previous; ln -s %(release)s current' % env)

 
def migrate():
    "Update the database"
    require('project_name')
    run('cd $(path)/releases/current/$(project_name);  ../../../bin/python manage.py syncdb --noinput')
 
