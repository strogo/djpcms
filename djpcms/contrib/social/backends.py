import os
import logging
from datetime import datetime
from hashlib import md5

from djpcms.contrib import social
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import UNUSABLE_PASSWORD

from .models import LinkedAccount, User


logger = logging.getLogger('djpcms.contrib.social')


def get_random_username():
    """Return hash from random string cut at 30 chars"""
    return md5(str(os.urandom(10))).hexdigest()[:30]


class SocialAuthBackend(ModelBackend):
    """A django.contrib.auth backend that authenticates the user based on
a authentication provider response"""

    def authenticate(self,
                     provider = None, response = None, token = None,
                     secret = None, user = None, **kwargs):
        from djpcms.conf import settings
        
        provider = social.get(provider)
        if not provider:
            return None
        
        name    = str(provider)
        objects = LinkedAccount.objects.select_related('user')
        user_available = True
        
        if user and user.is_authenticated():
            if not user.is_active:
                logger.warn('Inactive user %s trying to login with %s.' %(user,provider))
                return None
        else:
            user_available = False
            user = None
                
        # No user, no response but a token, we are trying to authenticate using a token
        if not user and not response and token:
            try:
                linked = objects.get(provider=name, token=token)
                return linked.user
            except LinkedAccount.DoesNotExist:
                return None
        
        if not (token and response):
            return None

        linked   = None
        details  = provider.get_user_details(response)
        uid      = str(details['uid'])
        if not user:
            username = self.get_unique_username(provider, details, response)
            try:
                linked = objects.get(provider=name,uid=uid)
                user = linked.user
            except LinkedAccount.DoesNotExist:
                if not getattr(settings, 'SOCIAL_AUTH_CREATE_USERS', False):
                    return None
                user = self.create_user(provider,details,response)
        else:
            username = self.get_username(provider, details, response)
           
        if not user_available:      
            if user.username != username:
                logger.warn('Trying to link user %s with %s provider. But the username is different from %s in the provider' %(user,provider,username))
                return None
        
        if not linked:
            linked = self.create_linked(user,uid,token,secret,provider,details)
            
        if not user_available:
            self.update_user_details(user, provider, details, response)
        return user

    
    def create_linked(self,user,uid,token,secret,provider,details):
        return LinkedAccount.objects.create(user=user,
                                            uid=uid,
                                            tokendate=datetime.now(),
                                            token=token,
                                            secret=secret,
                                            provider=str(provider),
                                            data=details)
        
    def get_username(self, provider, details, response):
        if 'username' in details:
            return details['username']
        else:
            return get_random_username()
            
    def get_unique_username(self, provider, details, response):
        """Return an unique username, if SOCIAL_AUTH_FORCE_RANDOM_USERNAME
        setting is True, then username will be a random 30 chars md5 hash
        """
        username = self.get_username(provider, details, response)

        name, idx = username, 2
        while True:
            try:
                User.objects.get(username=name)
                name = username + str(idx)
                idx += 1
            except User.DoesNotExist:
                username = name
                break
        return username

    def create_user(self, provider, details, response):
        username = self.get_username(provider, details, response)
        email = details.get('email', '')

        if hasattr(User.objects, 'create_user'): # auth.User
            user = User.objects.create_user(username, email)
        else: # create user setting password to an unusable value
            user = User.objects.create(username=username,
                                       email=email,
                                       password=UNUSABLE_PASSWORD)

        self.update_user_details(user, provider, details, response)
        return user

    def associate_auth(self, user, uid, provider, details, response):
        return LinkedAccount.objects.create(user=user,
                                            uid=uid,
                                            provider=str(provider),
                                            data=details)

    def update_user_details(self, user, provider, details, response):
        """Update user details with new (maybe) data"""
        fields = (name for name in ('first_name', 'last_name', 'email')
                        if user._meta.get_field(name))
        changed = False

        for name in fields:
            value = details.get(name)
            if value and value != getattr(user, name, value):
                setattr(user, name, value)
                changed = True

        if changed:
            user.save()

    def get_user(self, user_id):
        """Return user instance for @user_id"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
