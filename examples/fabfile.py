from djpcms.contrib.jdep.fabtools import *

def docs():
    '''Build documentation on the deployment server.'''
    import os
    import tarfile
    parent = lambda x : os.path.split(x)[0]
    path = os.curdir
    docs = os.path.join(path,'docs')
    json = os.path.join(docs,'build','json')
    local('cd %s; make json;' % docs)
    env.docfilename = 'djpcms-docs.tar.gz'
    t = tarfile.open(env.docfilename, mode = 'w:gz')
    t.add(json)
    t.close()
    put(env.docfilename, '%(path)s' % env)
    run('cd %(release_path)s && tar zxf ../%(docfilename)s' % env)
    run('rm %(path)s/%(docfilename)s' % env)
    local('rm %(docfilename)s' % env)


#utils.project('sitedjpcms','djpcms.com', apache_port = 93)
#env.redirects.append('www.djpcms.com')
#utils.after_deploy_hook.append(docs)


utils.project('sitedjpcms',
              'sbardella.homeip.net',
              server_type = 'nginx-twisted',
              #server_type = 'nginx-apache-mod_wsgi',
              redirect_port = 9011,
              #secure = True,
              #certificates='test-certificates',
              redirects = ['www.sbardella.homeip.net'])