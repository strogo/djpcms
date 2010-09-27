import os

from fabric.api import env, run, put, local, sudo

from djpcms.contrib.jdep.static import application_map

after_deploy_hook = []

# Target machine settings and configuration
defaults = {'server_type':        'nginx-apache-mod_wsgi',
            'server_user':        'www-data',
            'server_group':       'www-data',
            'server_name':        None,
            'threads':            15,
            'nginx_port':         80,
            'apache_port':        90,
            'path':               None,
            'project_name':       None,
            'with_site_packages': False,
            'server_admin':       None,
            'redirects':          []}


def project(module, domain_name, deploy_root_dir = 'deployment', setting_name = None, **kwargs):
    '''Setup django project for deployment using fabric.

* *module* is the name of the module containing the site. It must be on the same directory as the fabfile used to upload.
* *domain_name* the site domain name (for configuring web servers).
* *setting_name* optional settings file name (default is "settings").
* *deploy_root_dir* optional root directory where file will be installed (Default is "deployment").'''
    env.project = module
    env.domain_name = domain_name
    env.path = os.path.join(deploy_root_dir,module)
    env.setting_module = '%s.%s' % (module,setting_name or 'settings')
    os.environ['DJANGO_SETTINGS_MODULE'] = env.setting_module
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


def create_deploy():
    '''Create deploy object'''
    vrun('cd %(project_path)s; python manage.py deploy')
        
        
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


def install_environ(install_requirements = True):
    if env.get('with_site_packages',False):
        run('virtualenv %(release_path)s'% env)
    else:
        run('virtualenv --no-site-packages %(release_path)s' % env)
    if install_requirements:
        run('cd %(release_path)s; pip install -E . -r ./requirements.txt' % env)


def vrun(command = ''):
    '''Run a command in the server virtual environment.'''
    elem = 'cd %(release_path)s; source bin/activate' % env
    if command:
        elem = '%s; %s' % (elem,command)
    run(elem)


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
 
