from django.core.exceptions import *


class DjpcmsException(Exception):
    '''Base class for ``djpcms`` related exceptions.'''
    pass


class AlreadyRegistered(DjpcmsException):
    '''A :class:`DjpcmsException` raised when trying to register the same application twice.'''
    pass


class ModelException(DjpcmsException):
    '''A :class:`DjpcmsException` raised when a Model is not recognised.'''
    pass


class UsernameAlreadyAvailable(Exception):
    pass


class ApplicationUrlException(DjpcmsException):
    '''A :class:`DjpcmsException` raised when there are problems
related to urls configuration'''
    pass


class PageNotFound(DjpcmsException):
    '''A :class:`DjpcmsException` raised when page is not found.'''
    pass