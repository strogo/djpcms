import sys
import os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management import execute_manager


def _dumpfile(dir, app, format):
    return os.path.join(dir,'%s.%s' % (app,format))

def dumpmodule(dir,mod,val,format='json'):
    fn  = _dumpfile(dir,mod,format)
    srg = sys.argv[:]
    sys.stdout = sys.__stdout__
    print 'Writing %s' % fn
    f   = open(fn,'w')
    sys.stdout = f
    vals = tuple(val.split(' '))
    kw.update({'format': format})
    dump = dumpdata.Command()
    dump.handle(*vals, **kw)
    f.close()
    
def loadmodule(dir,mod,val,format='json'):
    fn  = _dumpfile(dir,mod,format)
    print 'Loading %s' % fn
    load = loaddata.Command()
    load.handle(fn)


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = "Runs this project as a Twisted.web2 application. Requires Twisted svn version."

    def handle(self, *args, **options):
        from django.conf import settings
        from django.utils import translation
        
        # Activate the current language, because it won't get activated later.
        try:
            translation.activate(settings.LANGUAGE_CODE)
        except AttributeError:
            pass
        
        N = len(args)
        if not N:
            raise ValueError
        else:
            command = args[0]
        
        # Get the module dump tuple
        mods = settings.DBMODULES_DUMP
        dumpdir = settings.DBMODULES_DUMPDIR
        mdic = dict(mods)
            
        if command == 'clear':
            from django.contrib.contenttypes.models import ContentType
            print 'cleaning Contenttypes'
            ContentType.objects.all().delete()
        else:
            if N > 1:
                mod = args[1]
            else:
                mod = None
                
            if command == 'dump':
                func = dumpmodule
            elif command == 'load':
                func = loadmodule
            else:
                raise ValueError
            
            if mod:
                val = mdic.get(mod,None)
                if val is None:
                    raise ValueError
                func(dumpdir,mod,val)
            else:
                for mod,val in mods:
                    func(dumpdir,mod,val)
            
            
        
    def usage(self, subcommand):
        return ''