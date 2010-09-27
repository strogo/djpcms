import os

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
    
    def handle(self, *args, **options):
        site = None
        user = None
        while not user:        
            username = prompt('username: ')
            password = prompt('password: ')
            user = authenticate(username = username, password = password)
            if not user or not user.is_active:
                user = None
                print("username or password not correct")
            
        comment  = prompt('comment: ')
        while not site:
            domain   = prompt('domain: ')
            site = Site.objects.filter(domain = domain)
            if not site:
                print("No such site domain: %s" % domain)
                
        dep = DeploySite(user = user, comment = comment, site = site[0])
        dep.save()
        
