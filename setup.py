
import os
from distutils.command.install import INSTALL_SCHEMES
from distutils.core import setup

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

def get_version():
    #path = os.path.dirname(__file__)
    #sys.path.insert(0,path)
    import djpcms
    return djpcms.get_version()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir    = os.path.dirname(__file__)
package_dir = os.path.join(root_dir, 'djpcms')
pieces = fullsplit(root_dir)
if pieces[-1] == '':
    len_root_dir = len(pieces) - 1
else:
    len_root_dir = len(pieces)

for dirpath, dirnames, filenames in os.walk(package_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)[len_root_dir:]))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])



setup(
        name         = 'djpcms',
        version      = get_version(),
        author       = 'Luca Sbardella',
        author_email = 'luca.sbardella@gmail.com',
        url          = 'http://github.com/lsbardel/djpcms',
        license      = 'BSD',
        description  = 'Dynamic content management system for Django',
        long_description = read('README.rst'),
        packages     = packages,
        data_files   = data_files,
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Framework :: Django',
            'Programming Language :: Python',
            'Programming Language :: JavaScript',
            'Topic :: Utilities'
        ],
    )

