from djpcms import sites
from djpcms.utils.importer import import_module


class TestEnvironment(object):
    '''Set up the test environment by checking which 3rd party
package is available'''

    def __init__(self, suite):
        sites.settings.DEBUG = False
        self.suite = suite
        self.libs = []
        self.check('django')
        self.check('werkzeug')
        self.check('sqlalchemy')
        self.setup()
        
    def check(self, name):
        try:
            import_module(name)
            self.libs.append(name)
        except ImportError:
            return None

    def setup(self):
        self._call('setup')
        
    def setupdb(self):
        self._call('setupdb')
        
    def teardown(self):
        self._call('teardown')
        
    def _call(self, funcname):
        for lib in self.libs:
            attname = '{0}_{1}'.format(funcname,lib)
            attr = getattr(self,attname,None)
            if attr:
                attr()
            
    def setup_django(self):
        from django.test.utils import setup_test_environment
        setup_test_environment()
        
    def setupdb_django(self):
        '''If django is available, setup django tests'''
        from django.db import connections
        old_names = []
        mirrors = []
        suite = self.suite
        for alias in connections:
            connection = connections[alias]
            # If the database is a test mirror, redirect it's connection
            # instead of creating a test database.
            if connection.settings_dict['TEST_MIRROR']:
                mirrors.append((alias, connection))
                mirror_alias = connection.settings_dict['TEST_MIRROR']
                connections._connections[alias] = connections[mirror_alias]
            else:
                old_names.append((connection, connection.settings_dict['NAME']))
                connection.creation.create_test_db(suite.verbosity, autoclobber=not suite.interactive)
        self.django_old_config = old_names, mirrors
        
    def teardown_django(self):
        '''If django is available, teardown django tests'''
        from django.test.utils import teardown_test_environment
        from django.db import connections
        teardown_test_environment()
        suite = self.suite
        old_names, mirrors = self.django_old_config
        # Point all the mirrors back to the originals
        for alias, connection in mirrors:
            connections._connections[alias] = connection
        # Destroy all the non-mirror databases
        for connection, old_name in old_names:
            connection.creation.destroy_test_db(old_name, suite.verbosity)
        
