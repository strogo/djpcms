from __future__ import with_statement

import os
from fabric.api import env, run, put, local, sudo

import utils
env.update(utils.defaults)


def archive(release = True):
    '''Create a .tar.gz archive of the project directory.
The :func:`djpcms.contrib.jdep.utils.project` must have been called already
with the name of the project.'''
    import os
    import tarfile
    from django.template import loader, mark_safe
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
    "Upload the ``project`` directory into the server"
    import time
    import os
    if release and not env.path.startswith('/'):
        result = run('pwd').split(' ')[0]
        env.path = os.path.join(result,env.path)
        
    release_name = time.strftime('%Y%m%d-%H%M%S')    
    utils.get_directories(release_name, release)
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
    from static import server_types
    server = server_types[env.server_type]
    server.reboot()
        
        
def deploy(release = True):
    '''Deploy site to the server'''
    if release:
        env.site_username = utils.prompt('site username: ')
        env.site_password = utils.prompt('site password: ')
    from static import server_types
    setup(release)
    if release:
        utils.install_environ(release)
    server = server_types[env.server_type]
    server.install(release)
    if release:
        utils.create_deploy()
    # call functions in after deploy hook
    for hook in utils.after_deploy_hook:
        hook()
    #.reboot()
    if not release:
        return server.result
    
    
def serverconfig():
    '''Create server configuration files on local directory'''
    from static import server_types
    env.path = ''
    server = server_types[env.server_type]
    utils.get_directories(release = False)
    server.config_files(env, dir = '.')
    
def info():
    '''Information regarding installation parameters'''
    from static import server_types
    utils.get_directories(release = False)
    data = env.copy()
    server = server_types[env.server_type]
    server.info(data)
    for k in sorted(data):
        print('%20s: %s' % (k,data[k]))
    
    
def host_type():
    '''type of operative system on the host machine
    '''
    run('uname -s')

