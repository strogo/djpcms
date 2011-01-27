# Uniforms Layout is the Default layout
from djpcms.core.exceptions import DjpcmsException
from .layout.uniforms import Layout as DefaultLayout

__all__ = ['FormException',
           'ValidationError',
           'DefaultLayout']


class FormException(DjpcmsException):
    pass


class ValidationError(Exception):
    pass
