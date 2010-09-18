import os
from django.template import loader
from fabric.api import env, run, put, local, sudo


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
    '''Create a configuration file from template
    @param fname: one of nginx, mod_wsgi, mod_python, django
    @param ext: conf or wsgi
    @param dir: directory containing the file or None. If none the __file__ directory is used
    @return: file name
    '''
    filename = 'jdep/{0[project_name]}_{1}.{2}'.format(env,fname,ext)
    data = loader.render_to_string(filename,env)
    dir = dir or os.path.dirname(__file__)
    data = open('{2}/{0}.{1}'.format(fname,ext,dir),'r').read()
    ngdata = data.format(env)
    f = open(filename,'w')
    f.write(ngdata)
    f.close()
    return filename



class ServerInstaller(object):
    pass


class nginx_apache_wsgi(ServerInstaller):

    def __str__(self):
        return 'nginx + apache (mod_wsgi)'
    
    def install(self):
        env.nginx_assess_log = '%(release_path)s/logs/nginx_access.log' % env
        
        nginx  = config_file('nginx')
        apache = config_file('mod_wsgi')
        wsgi   = config_file('django','wsgi')
    
        release = '{0[path]}/releases/{0[release]}'.format(env)
        put(nginx, release)
        local('rm {0}'.format(nginx))
        put(apache, release)
        local('rm {0}'.format(apache))
        if wsgi:
            put(wsgi,release)
            local('rm {0}'.format(wsgi))
        
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
 
