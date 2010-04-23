#
# fab tools used by fabric to install a virtualenv.
#
# Only Ubuntu server supported for now
#
# Usage:
#
# fab <setting> <command> run command on setting
#
# Example of setting is
#
#
#def myserver():
#    env.hosts            = ['myserver.com']
#    env.virtualhost_path = "/"
#    env.version          = '2.5'
#    env.path             = '/home/%(user)s/deployment/%(server_name)s' % env
#
# command
#    clear             completely remove the virtual environment
#    setup             clear and create a new virtual environment
#    deploy            add requirements and set up web servers. The environment must be available
#    clearanddeploy    run setup and deploy in one go
#
#
from __future__ import with_statement # needed for python 2.5
import os

from django.template import loader
from django.contrib.auth import authenticate

from fabric.api import *

from models import DeploySite

#___________________________________________________________ SETTINGS DEFAULT
env.module_name      = None          # Specify the module which contain the settings file
env.project_name     = None          # if None it will be set to server_name, only used for local testing really!
env.no_site_packages = False

# Target machine settings and configuration
target = {'system':             'p',          #p for POSIX, w for WINDOWS  
          'server_type':        'mod_wsgi',   #mod_wsgi or mod_python for now
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


def initialize():
    base  = target.get('path',None)
    pname = target.get('project_name',None)
    if base and pname:
        path = '%s/%s' % (base,pname)
        #if target.get('system','p') == 'p':
        #    path = os.path.join(base,pname)
        #else:
        #    path = '%s//%s' % (base,pname)
        env.path = path
    else:
        raise ValueError('Target path not specified')
    env.host_string = target.get('host',target.get('server_name',None))
    

def clear():
    '''
    remove the environment
    '''
    run('cd {0[path]}'.format(target))
    #initialize()
    #comm = run
    #if target.get('system','p') == 'p':
    #    comm = sudo
        
    #comm('rm -rf {0[path]}'.format(env))
    #run('cd {0[path]}'.format(target))
    #run('pwd')
    #comm('mkdir {0[project_name]}'.format(target))


def setup():
    '''
    Initialize the virtual environment
    '''
    clear()
    #if target.get('no_site_packages',False):
    #    run('virtualenv --no-site-packages %(path)s' % env)
    #else:
    #    run('virtualenv {0[project_name]}'.format(target))
    #run('mkdir {0[path]}/releases'.format(env))
    #target['logdir'] = '{0[path]}/logs'.format(env)
    #run('mkdir {0}'.format(env.logdir))
    #if target.get('server_user',None):
    #    sudo('chown {0[server_user]}:{0[server_group]} -R {0[logdir]}'.format(target))
    

def install_site():
    '''
    First create link to django admin static files
    Second Create nginx and apache configuration files
    '''
    run('rm -rf {0[path]}/media/django_admin'.format(env))
    run('ln -s {0[python_path]}/django/contrib/admin/media {0[path]}/media/django_admin'.format(env))
    
    env.nginx_assess_log = '{0[path]}/logs/nginx_access.log'
    
    nginx  = config_file('nginx')
    
    wsgi = None
    if env.server_type == 'mod_wsgi':
        apache = config_file('mod_wsgi')
        wsgi   = config_file('django','wsgi')
    else:
        apache = config_file('mod_python')

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


def clearanddeploy():
    setup()
    deploy()    


def reboot():
    "Reboot web servers"
    sudo("/etc/init.d/nginx restart")
    sudo('/etc/init.d/apache2 restart')
    

def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and 
    then restart the webserver
    """
    username = prompt('username: ')
    password = prompt('password: ')
    comment  = prompt('comment: ')
    user = authenticate(username = username, password = password)
    if user is not None and user.is_active:
        dep = DeploySite(user = user, comment = comment)
        dep.save()
    else:
        exit(1)
        
    import time
    try:
        env.release = time.strftime('%Y%m%d-%H%M%S')
        python_path()
        upload_tar_from_git()
        install_requirements()
        install_site()
        symlink_current_release()
        #migrate()
        reboot()
    except:
        dep.delete()


def python_version():
    initialize()
    return run('python --version')

def python_path():
    env.python_path = '{0[path]}/lib/python{0[version]}/site-packages'.format(env)
    
def host_type():
    '''
    type of operative system on the host machine
    '''
    run('uname -s')


def git_pull():
    "Updates the repository."
    run("cd ~/git/$(repo)/; git pull $(parent) $(branch)")


def git_reset():
    "Resets the repository to specified version."
    run("cd ~/git/$(repo)/; git reset --hard $(hash)")

#
#____________________________________________ UTILITIES


def symlink(origin, target):
    run('ln -s {0} {1}')


def config_file(fname, ext = 'conf', dir = None):
    '''
    Create a configuration file from template
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
    
    
def install_requirements():
    "Install the required packages from the requirements file using pip"
    run('cd %(path)s; pip install -E . -r ./releases/%(release)s/requirements.txt' % env)


def symlink_current_release():
    "Symlink our current release"
    run('cd %(path)s/releases; rm previous; mv current previous; ln -s %(release)s current' % env)

 
def migrate():
    "Update the database"
    require('project_name')
    run('cd $(path)/releases/current/$(project_name);  ../../../bin/python manage.py syncdb --noinput')
 