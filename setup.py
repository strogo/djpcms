version = (0, 4, 'pre')

import os
from quickutils import packages_in_dirs, get_version

from distutils.command.install import INSTALL_SCHEMES
from distutils.core import setup

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


root_dir    = os.path.dirname(__file__)
packages, data_files = packages_in_dirs(root_dir, 'djpcms')


setup(
        name = 'djpcms',
        version = get_version(version),
        author = 'Luca Sbardella',
        author_email = 'luca@quantmind.com',
        url = 'http://code.google.com/p/txdjango/',
        license = 'New BSD License',
        description = 'Django-jQuery dynamic Content Management System',
        packages = packages,
        data_files = data_files,
        install_requires = [ "django" ],
        keywords = 'django, cms',
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: New BSD License',
            'Operating System :: OS Independent',
            'Framework :: Django',
            'Programming Language :: Python',
            'Topic :: Software Development :: Utilities'
        ]
    )

