import os
from hashlib import md5

from djpcms.contrib import social
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import UNUSABLE_PASSWORD

from .models import LinkedAccount, User

def get_random_username():
    """Return hash from random string cut at 30 chars"""
    return md5.md5(str(os.urandom(10))).hexdigest()[:30]


class SocialAuthBackend(ModelBackend):
    """A django.contrib.auth backend that authenticates the user based on
a authentication provider response"""

    def authenticate(self, *args, **kwargs):
        """Authenticate user using social credentials

        Authentication is made if this is the correct backend, backend
        verification is made by kwargs inspection for current backend
        name presence.
        """
        from djpcms.conf import settings
        provider = social.get(kwargs.get('provider',None))
        if not provider:
            return None

        name     = str(provider)
        response = kwargs.get('response')
        details  = provider.get_user_details(response)
        uid      = details['uid']
        #uid      = str(provider.get_user_id(details, response))
        try:
            auth_user = LinkedAccount.objects.select_related('user').get(provider=name,uid=uid)
        except LinkedAccount.DoesNotExist:
            if not getattr(settings, 'SOCIAL_AUTH_CREATE_USERS', False):
                return None
            user = self.create_user(provider=provider,details=details, *args, **kwargs)
        else:
            user = auth_user.user
            provider.update_user_details(user, details)
        return user

    def get_uid(self, provider, details, response):
        return str(provider.get_user_id(details, response))
    
    def get_username(self, provider, details, response):
        """Return an unique username, if SOCIAL_AUTH_FORCE_RANDOM_USERNAME
        setting is True, then username will be a random 30 chars md5 hash
        """
        if 'username' in details:
            username = details['username']
        else:
            username = get_random_username()

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

    def create_user(self, response, provider, details, *args, **kwargs):
        """Create user with unique username. New social credentials are
        associated with @user if this parameter is not None."""
        user = kwargs.get('user')
        if user is None: # create user, otherwise associate the new credential
            username = self.get_username(provider, details, response)
            email = details.get('email', '')

            if hasattr(User.objects, 'create_user'): # auth.User
                user = User.objects.create_user(username, email)
            else: # create user setting password to an unusable value
                user = User.objects.create(username=username, email=email,
                                           password=UNUSABLE_PASSWORD)

        # update details and associate account with social credentials
        self.update_user_details(user, provider, details, response)
        self.associate_auth(user, provider, details, response)
        return user

    def associate_auth(self, user, provider, response, details):
        """Associate an OAuth with a user account."""
        # Check to see if this OAuth has already been claimed.
        uid = self.get_uid(provider, reponse)
        try:
            user_social = LinkedAccount.objects.select_related('user')\
                                                .get(provider=self.name,
                                                     uid=uid)
        except LinkedAccount.DoesNotExist:
            if getattr(settings, 'SOCIAL_AUTH_EXTRA_DATA', True):
                extra_data = self.extra_data(user, uid, response, details)
            else:
                extra_data = ''
            user_social = UserSocialAuth.objects.create(user=user, uid=uid,
                                                        provider=self.name,
                                                        extra_data=extra_data)
        else:
            if user_social.user != user:
                raise ValueError, 'Identity already claimed'
        return user_social

    def update_user_details(self, user, details):
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
