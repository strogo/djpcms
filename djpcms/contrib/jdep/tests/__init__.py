import os
import datetime

from django.test import TestCase
from django.conf import settings
from djpcms.contrib.jdep.fabtools import *

split = os.path.split


class Deployment(TestCase):
    
    def setUp(self):
        self.curdir = os.getcwd()
        os.chdir(os.path.split(os.path.abspath(__file__))[0])
        env.host_string = 'localhost'
        utils.project('testjdep','testjdep.com', apache_port = 103)
    
    def testPath(self):
        upload(False)
        self.assertEqual(env.project,'testjdep')
        self.assertEqual(env.domain_name,'testjdep.com')
        self.assertTrue(env.release)
        self.assertTrue(env.release_path)
        
    def testServer(self):
        upload(False)
        result = utils.install_site(False)
        self.assertTrue(env.logdir)
        self.assertTrue(env.confdir)
        self.assertEqual(split(env.logdir)[0],split(env.confdir)[0])
        nginx = result['nginx']
        self.assertTrue('server_name  %s' % env.domain_name in nginx)
        self.assertTrue('access_log   %s' % env.nginx_assess_log in nginx)
        self.assertTrue('proxy_pass http://127.0.0.1:103/;' in nginx)
        
    def tearDown(self):
        os.chdir(self.curdir)