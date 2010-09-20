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
    from django.template import loader
    from djpcms.utils import mark_safe
    utils.rmfiles(os.curdir, ext = 'pyc')
    filename = '%s.tar.gz' % env.project
    data = loader.render_to_string('jdep/server.txt', {'env':mark_safe('%s\n' % env), 'release': release})
    if release:
        f = open('server.py','w')
        f.write(data)
        f.close()
        t = tarfile.open(filename, mode = 'w:gz')
        t.add(env.project)
        t.add('requirements.txt')
        t.add('__init__.py')
        t.add('server.py')
        t.close()
        local('rm server.py')
    else:
        env.server_script = data
    return filename


def upload(release = True):
    "Upload the site to the server"
    import time
    import os
    if release and not env.path.startswith('/'):
        result = run('pwd').split(' ')[0]
        env.path = os.path.join(result,env.path)
        
    env.release = time.strftime('%Y%m%d-%H%M%S')
    env.release_path = '%(path)s/%(release)s' % env
    env.project_path = os.path.join(env.release_path,env.project)
    env.logdir  = os.path.join(env.release_path,'logs')
    env.confdir = os.path.join(env.release_path,'conf')
    env.tarfile = archive(release)
    # put tar package
    if release:
        utils.makedir(env.release_path)
        run('cd; mkdir %(logdir)s; mkdir %(confdir)s' % env)
        put(env.tarfile, '%(path)s' % env)
        run('cd %(release_path)s && tar zxf ../%(tarfile)s' % env)
        run('rm %(path)s/%(tarfile)s' % env)
        local('rm %(tarfile)s' % env)


def clear():
    '''Clear the whole installation directory'''
    run('rm -rf %(path)s' % env)

    
def setup(release = True):
    '''Install the site and requirements on server
    '''
    upload(release)
    if release:
        utils.install_environ(True)
    

def reboot():
    "Reboot web servers"
    installer = utils.server_types[env.server_type]
    server.reboot()
    

def syncdb():
    '''Syncdb on the server.'''
    setup()
    utils.startvirtualenv()
    run('cd %(release_path)s/%(project)s; python manage.py syncdb' % env)
        
        
def deploy(release = True):
    '''Deploy site to the server'''
    #the latest version of the site to the servers, install any
    #required third party modules, install the virtual host and 
    #then restart the webserver
    #username = prompt('site username: ')
    #password = prompt('site password: ')
    #comment  = prompt('comment: ')
    from static import server_types
    setup(release)
    if release:
        utils.install_environ(release)
    server = server_types[env.server_type]
    server.install(release)
    #.reboot()
    if not release:
        return server.result
    
    
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

