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


class NoData(object):
    def __repr__(self):
        return '<NoData>'
    __str__ = __repr__


nodata = NoData()
