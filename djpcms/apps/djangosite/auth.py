from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import authenticate, login, logout


def hack_django_user():
    User.athenticate = authenticate
    User.logout = logout