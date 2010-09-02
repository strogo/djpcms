from django.core.exceptions import *

class UsernameAlreadyAvailable(Exception):
    pass


class ApplicationUrlException(Exception):
    pass


class PageNotFound(Exception):
    pass