import os
import sys
import optparse

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate

from djpcms.contrib.jdep.models import DeploySite


def prompt(text, default=''):
    '''Prompt to input in the console.'''
    default_str = ''
    if default != '':
        default_str = ' [%s] ' % str(default).strip()
    else:
        default_str = ' '
    prompt_str = text.strip() + default_str
    return raw_input(prompt_str) or default

 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            "-u", "--username", 
            dest="username", 
            action="store",
            default=None, 
            help="Username"
        ),
        optparse.make_option(
            "-p", "--password", 
            dest="password", 
            action="store",
            default=None, 
            help="User Password"
        ),
        optparse.make_option(
            "-d", "--domain", 
            dest="domain", 
            action="store",
            default=None, 
            help="Web site domain name"
        ),
        optparse.make_option(
            "-c", "--comment", 
            dest="comment", 
            action="store",
            default="", 
            help="Deploy Comment"
        ))
    
    help = "Add deploy timestamp to database"     
    
    def handle(self, *args, **options):
        stdout   = options.get('stdout',sys.stdout)
        username = options.get('username', None)
        password = options.get('password', None)
        user = None
        if username and password:
            user = authenticate(username = username, password = password)
        if not user:
            stdout.write('no user. nothing done.')
            return
        comment = options.get('comment','')
        site = Site.objects.filter(domain = options.get('domain',''))
        if not site:
            stdout.write('no site. nothing done.')
            return
        dep = DeploySite(user = user, comment = comment, site = site[0])
        dep.save()
        stdout.write('ok. %s deployed %s.' % (dep.user.username,dep.site.domain))
        
