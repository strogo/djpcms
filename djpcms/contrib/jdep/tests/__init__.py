import os
import sys
import datetime

from django.test import TestCase
from django.conf import settings
from djpcms.contrib.jdep.fabtools import *

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
        nginx = deploy(False)['nginx']
        self.assertTrue(env.apps)
        media_inconf = 0
        for app in env.apps:
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
        self.assertTrue('access_log   %s' % env.nginx_assess_log in nginx)
        self.assertTrue('proxy_pass http://127.0.0.1:103/;' in nginx)
        
    def tearDown(self):
        os.chdir(self.curdir)