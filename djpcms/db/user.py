from django.contrib.auth.models import User, AnonymousUser , Group

__init__ = ['authenticate','get_full_user']

def authenticate(username, password):
    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)
    if not user:
        return AnonymousUser()
    else:
        return user
    
    
def get_full_user(user):
    if not isinstance(user,User):
        try:
            user = User.objects.get(username = str(user))
        except:
            user = AnonymousUser()
            
    if not isinstance(user,User):
        user = AnonymousUser()
        user.preference = None
    
    else:
        try:
            user.preference = user.get_profile()
            return user
        except:
            user.preference = None
            return user