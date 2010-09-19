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
from __future__ import with_statement

from fabric.api import env, run, put, local, sudo
import utils
env.update(utils.defaults)    


def archive(release = True):
    '''Create a .tar.gz archive of the project directory.
The :func:`djpcms.contrib.jdep.utils.project` must have been called already
with the name of the project.'''
    import os
    import tarfile
    utils.rmfiles(os.curdir, ext = 'pyc')
    filename = '%s.tar.gz' % env.project
    if release:
        t = tarfile.open(filename, mode = 'w:gz')
        t.add(env.project)
        t.add('requirements.txt')
        t.close()
    return filename


def upload(release = True):
    "Upload the site to the server"
    import time
    env.tarfile = archive()
    env.release = time.strftime('%Y%m%d-%H%M%S')
    env.release_path = '%(path)s/%(release)s' % env
    # put tar package
    if release:
        utils.makedir(env.release_path)
        put(env.tarfile, '%(path)s' % env)
        run('cd %(release_path)s && tar zxf ../%(tarfile)s' % env)
        run('rm %(path)s/%(tarfile)s' % env)
        local('rm %(tarfile)s' % env)


def clear():
    '''Clear the whole installation directory'''
    run('rm -rf %(path)s' % env)

    
def setup():
    '''Install the site and requirements on server
    '''
    upload()
    if env.get('with_site_packages',False):
        run('virtualenv %(release_path)s'% env)
    else:
        run('virtualenv --no-site-packages %(release_path)s' % env)
    run('cd %(release_path)s; pip install -E . -r ./requirements.txt' % env)
    

def reboot():
    "Reboot web servers"
    installer = utils.server_types[env.server_type]
    server.reboot()
    

def syncdb():
    '''Syncdb on the server.'''
    setup()
    utils.startvirtualenv()
    run('cd %(release_path)s/%(project)s; python manage.py syncdb' % env)
        
        
def deploy():
    '''Deploy site to the server'''
    #the latest version of the site to the servers, install any
    #required third party modules, install the virtual host and 
    #then restart the webserver
    #username = prompt('site username: ')
    #password = prompt('site password: ')
    #comment  = prompt('comment: ')
    setup()
    utils.install_site()
    
    
def info():
    '''Information regarding installation parameters'''
    server = utils.server_types[env.server_type]
    print('site module:        %(project)s' % env)
    print('site domain:        %(domain_name)s' % env)
    print('location on server: %(path)s' % env)
    print('server type:        %s' % server)
    server.info()
    
    
def host_type():
    '''type of operative system on the host machine
    '''
    run('uname -s')

