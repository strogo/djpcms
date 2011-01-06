from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from djpcms.apps.included.user import UserInterface


class DjangoUser(UserInterface):
    
    def __init__(self, userobj = None, **kwargs):
        if userobj:
            self._underlying = userobj
        else:
            self._underlying = User(**kwargs)
        
    def underlying(self):
        return self._underlying
    
    def is_authenticated(self):
        return self._underlying.is_authenticated()
    
    def is_active(self):
        return self._underlying.is_active
    
    def is_superuser(self):
        return self._underlying.is_superuser
    
    def save(self):
        return self._underlying.save()
    
    def login(self, request):
        return login(request, self._underlying)
    
    @classmethod
    def modelclass(cls):
        return User
    
    @classmethod
    def create(cls, *args, **kwargs):
        return User.objects.create_user(*args, **kwargs)
    
    @classmethod
    def create_super(cls, *args, **kwargs):
        return User.objects.create_superuser(*args, **kwargs)
    
    @classmethod
    def authenticate(cls, *args, **kwargs):
        user = authenticate(*args, **kwargs)
        return cls(userobj = user)
    
    @classmethod
    def logout(cls, request):
        return logout(request)
    