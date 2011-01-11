

class DjpcmsException(Exception):
    '''Base class for ``djpcms`` related exceptions.'''
    pass


class ImproperlyConfigured(DjpcmsException):
    '''A :class:`DjpcmsException` raised when djpcms has inconsistent configuration.'''
    pass


class ViewDoesNotExist(DjpcmsException):
    '''A :class:`DjpcmsException` raised when a view instance does not exist.'''
    pass


class PermissionDenied(DjpcmsException):
    '''A :class:`DjpcmsException` raised when permission is not met.'''
    pass


class CommandError(ImproperlyConfigured):
    '''A :class:`DjpcmsException` raised when a management command throws an error.'''
    pass


class AlreadyRegistered(DjpcmsException):
    '''A :class:`DjpcmsException` raised when trying to register the same application twice.'''
    pass


class ModelException(DjpcmsException):
    '''A :class:`DjpcmsException` raised when a Model is not recognised.'''
    pass


class ObjectDoesNotExist(ModelException):
    '''A :class:`ModelException` raised when an instance of a required model class
does not exists.'''
    pass

class UsernameAlreadyAvailable(Exception):
    pass


class ApplicationUrlException(DjpcmsException):
    '''A :class:`DjpcmsException` raised when there are problems
related to urls configuration'''
    pass


class ApplicationNotAvailable(DjpcmsException):
    '''A :class:`DjpcmsException` raised when a requested application is not available.'''
    pass

class PageException(DjpcmsException):
    '''A :class:`DjpcmsException` for pages.'''
    pass


class PageNotFound(PageException):
    '''A :class:`PageException` raised when page is not found.'''
    pass


class BlockOutOfBound(PageException):
    '''A :class:`PageException` raised when requesting a block not available in page.'''
    pass
    