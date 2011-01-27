# Uniforms Layout is the Default layout
from .layout.uniforms import Layout as DefaultLayout

__all__ = ['ValidationError',
           'DefaultLayout',
           'nodata']


class NoData(object):
    def __repr__(self):
        return '<NoData>'
    __str__ = __repr__


class ValidationError(Exception):
    pass

nodata = NoData()