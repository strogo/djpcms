#
# Required by Cython to build extensions
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules  = Extension('djpcms.lib.djp', ['lib/src/djp.pyx'])

libparams = {
             'ext_modules': [ext_modules],
             'cmdclass': {'build_ext' : build_ext},
             }
