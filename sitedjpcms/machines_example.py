
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
# Set vespa machine to be a development machine
SiteMachine(name = 'vespa', debug = True, servs = True)


class Identity(object):
    
    def __init__(self):
        self.SECRET_KEY          = 'q*+zqx@*%r_&7)iney)od2j*9py=n6l#_u^vms^(om&avn_8=='
        self.ADMIN_URL_PREFIX    = '/admin/'
        self.GOOGLE_ANALYTICS_ID = None
        
        self.TWITTER_CONSUMER_KEY       = ''
        self.TWITTER_CONSUMER_SECRET    = ''