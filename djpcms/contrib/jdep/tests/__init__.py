import os
import sys
import datetime

from django.test import TestCase
from django.conf import settings

try:
    from djpcms.contrib.jdep.fabtools import *
    fabric_available = True
except ImportError:
    fabric_available = False


if fabric_available:
    split = os.path.split

    class Deployment(TestCase):
        
        def setUp(self):
            self.curdir = os.getcwd()
            path = os.path.split(os.path.abspath(__file__))[0]
            os.chdir(path)
            if path not in sys.path:
                sys.path.insert(0,path)
            env.host_string = 'localhost'
            utils.project('testjdep','testjdep.com', apache_port = 103)
        
        def testPath(self):
            upload(False)
            self.assertEqual(env.project,'testjdep')
            self.assertEqual(env.domain_name,'testjdep.com')
            self.assertTrue(env.release)
            self.assertTrue(env.release_path)
            
        def testApps(self):
            result = deploy(False)
            nginx  = result['nginx']
            apps   = result['apps']
            self.assertTrue(apps)
            media_inconf = 0
            self.assertTrue(env.project_path in nginx)
            for app in apps:
                if app.exists:
                    media_inconf += 1
                    self.assertTrue('location %s {' % app.url() in nginx)
                    self.assertTrue(app.base in nginx)
            self.assertEqual(media_inconf,2)
            
        def testServer(self):
            result = deploy(False)
            self.assertTrue(env.logdir)
            self.assertTrue(env.confdir)
            self.assertEqual(split(env.logdir)[0],split(env.confdir)[0])
            nginx = result['nginx']
            self.assertTrue('server_name  %s' % env.domain_name in nginx)
            self.assertTrue('access_log   %s' % env.logdir in nginx)
            self.assertTrue('listen       %s' % env.nginx_port in nginx)
            self.assertTrue('proxy_pass http://127.0.0.1:103/;' in nginx)
            
        def testApache(self):
            result = deploy(False)
            apache = result['apache']
            self.assertTrue('ServerName %s' % env.domain_name in apache)
            
        def tearDown(self):
            os.chdir(self.curdir)
            
