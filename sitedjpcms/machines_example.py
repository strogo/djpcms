
from djpcms.utils.machines import machine, get_machine

class SiteMachine(machine):
    '''
    The default for this site application
    '''
    def __init__(self,
                 dbname     = 'sampledb',
                 dbengine   = 'sqlite3',
                 dbuser     = '',
                 dbpassword = '',
                  **kwargs):
        super(SiteMachine,self).__init__(dbname = dbname,
                                         dbengine = dbengine,
                                         dbuser = dbuser,
                                         dbpassword = dbpassword,
                                         **kwargs)
        
SiteMachine()
SiteMachine(name = 'vespa', servs = True)


class Identity(object):
    
    def __init__(self):
        self.SECRET_KEY          = '@anu(%l86dlk=^yb8%r1izr6^c$755+^*4-*db^3&!^o&khh1$'
        self.ADMIN_URL_PREFIX    = '/admin/'
        self.GOOGLE_ANALYTICS_ID = None