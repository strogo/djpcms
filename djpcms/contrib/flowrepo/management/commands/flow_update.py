import logging
import optparse
import flowrepo.providers
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            "-p", "--provider", 
            dest="providers", 
            action="append", 
            help="Only use certain provider(s)."
        ),
        optparse.make_option(
            "-l", "--list-providers", 
            action="store_true", 
            help="Display a list of active data providers."
        ),
        optparse.make_option(
            "-c", "--cleanupdate", 
            action="store_true", 
            help="Remove all Item and perform a new update"
        ),
    )
    
    def handle(self, *args, **options):
        level = {
            '0': logging.WARN, 
            '1': logging.INFO, 
            '2': logging.DEBUG
        }[options.get('verbosity', '0')]
        logging.basicConfig(level=level, format="%(name)s: %(levelname)s: %(message)s")
        
        c  = options.get('cleanupdate', False)
        
        if options['list_providers']:
            self.print_providers()
            return 0

        if options['providers']:
            for provider in options['providers']:
                if provider not in self.available_providers():
                    print "Invalid provider: %r" % provider
                    self.print_providers()
                    return 0

        flowrepo.providers.update(options['providers'],c)

    def available_providers(self):
        return flowrepo.providers.active_providers()

    def print_providers(self):
        available = sorted(self.available_providers().keys())
        print "Available data providers:"
        for provider in available:
            print "   ", provider
        
