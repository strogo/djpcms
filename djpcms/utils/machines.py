
import os
import platform

class machine(object):
    '''
    Utility class for defining server machines
    '''
    _machines = {}
    
    def __init__(self,
                 name       = 'default',
                 dev        = False,
                 servs      = False,
                 dbengine   = 'postgresql_psycopg2',  #'postgresql_psycopg2',
                 dbhost     = 'localhost',
                 dbport     = 5432,
                 tempdir    = '.',
                 dbname     = None,
                 dbuser     = None,
                 dbpassword = None,
                 cache      = 'dummy:///',
                 dboptions  = None,
                 egg_cache  = '/var/www/.python-eggs',
                 media_root = '/var/www/djangosites/media'
                 ):
        self.dbengine    = dbengine
        self.dbhost      = dbhost
        self.dbport      = str(dbport)
        self.dbname      = dbname
        self.dbuser      = dbuser
        self.dbpassword  = dbpassword
        self.cache       = cache
        self.tempdir     = tempdir
        self.machine     = None
        self.servs       = servs
        self.dev         = dev
        self.dboptions   = dboptions
        self.egg_cache   = egg_cache
        self._media_root = media_root
        self._machines[name] = self
        
    def media_root(self):
        if self.servs:
            return os.path.join(self.LOCDIR,'media')
        else:
            return self._media_root
            
            
        



def get_machine(pdir):
    node = platform.node()
    node = node.split('.')[0]
    default = machine._machines.get('default', None)
    sett = machine._machines.get(node, default)
    if not sett:
        raise ValueError('machine %s setting not available' % node)
    sett.machine = node
    sett.LOCDIR  = pdir
    return sett