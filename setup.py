
import os
import sys
from setuptools import setup, find_packages

def get_version():
    path = os.path.dirname(__file__)
    sys.path.insert(0,path)
    import djpcms
    return djpcms.get_version()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
        name         = 'djpcms',
        version      = get_version(),
        author       = 'Luca Sbardella',
        author_email = 'luca.sbardella@gmail.com',
        url          = 'http://github.com/lsbardel/djpcms',
        license      = 'BSD',
        description  = 'Dynamic content management system for Django',
        long_description = read('README'),
        packages     = find_packages('djpcms'),
        #data_files   = data_files,
        install_requires = [
                            'django-tagging==0.4pre',
                            'Django>=1.1',
                            'setuptools'
                            ],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: New BSD License',
            'Operating System :: OS Independent',
            'Framework :: Django',
            'Programming Language :: Python',
            'Topic :: Software Development :: Utilities'
        ],
    )

