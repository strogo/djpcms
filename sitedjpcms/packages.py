
import sys
import os

class install(object):
    
    def __init__(self, serv = None):
        try:
            import djpcms
        except:
            sys.path.append('..')
            import djpcms
    
        self.LOCDIR    = os.path.dirname(__file__)
        
        if not serv:
            cd = os.getcwd()
            os.chdir(os.pardir)
            path = os.getcwd()
            self.MEDIA_ROOT  = os.path.join(path,'media')
            os.chdir(cd)
        else:
            self.MEDIA_ROOT  = serv
    
    #PS.local_apps    = putils.adddir(PS.LOCDIR, 'apps')
    #PS.local_plugins = putils.adddir(PS.LOCDIR, 'plugins')
    
    