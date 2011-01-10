from djpcms import sites
from djpcms.utils.importer import module_attribute
from djpcms.core.models import ModelInterface

__all__ = ['User',
           'UserInterface',
           'AnonymousUser',
           'UserClass',
           'CreateUser',
           'AddUserImplementation']


_user_implementations = {'django':'djpcms.apps.djangosite.auth.DjangoUser'}


class UserInterface(ModelInterface):
    '''General interface for users. It can be used as a'''
    
    def is_authenticated(self):
        raise NotImplementedError
    
    def is_active(self):
        raise NotImplementedError
    
    def is_anonymous(self):
        return False
    
    def is_superuser(self):
        return False
    
    def login(self, request):
        raise NotImplementedError
    
    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def create_super(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def authenticate(cls, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def logout(cls, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def get(cls, **kwargs):
        raise NotImplementedError


class AnonymousUser(UserInterface):
    
    def __init__(self, **kwargs):
        pass
    
    def is_authenticated(self):
        raise False
    
    def is_anonymous(self):
        return True
    
    def is_active(self):
        raise True
    
    def save(self):
        pass
    
    def login(self, request):
        pass
    
    @classmethod
    def authenticate(cls, **kwargs):
        return False
    
    @classmethod
    def logout(cls, **kwargs):
        pass


def UserClass():
    global _user_implementations
    mod = sites.settings.USER_MODEL
    if mod:
        impl = _user_implementations.get(mod,AnonymousUser)
        if isinstance(impl,str):
            impl = module_attribute(impl)
            _user_implementations[mod] = impl
        return impl
    else:
        return AnonymousUser
    
    
def User(**kwargs):
    ucls = UserClass()
    if ucls:
        return ucls(**kwargs)
    else:
        return None
    
    
def CreateUser(**kwargs):
    ucls = User(**kwargs)
    u = ucls(**kwargs)
    u.save()


def AddUserImplementation(name, location):
    if name not in _user_implementations:
        _user_implementations[name] = location
        
