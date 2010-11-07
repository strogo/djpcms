import os
import glob
import logging
from flowrepo import settings

log = logging.getLogger("flowrepo.update")

_providers = {}

def active_providers():
    """
    Return a dict of {name: module} of active, enabled providers.
    """
    global _providers
    if _providers == None:
        return {}
    if _providers:
        return _providers
    providers = {}
    for provider in settings.FLOWREPO_PROVIDERS:
        if provider.endswith('.*'):
            to_load = expand_star(provider)
        else:
            to_load = [provider]
        for p in to_load:
            try:
                mod = __import__(p, '', '', [''])
            except ImportError, e:
                log.error("Couldn't import provider %r: %s" % (p, e))
            else:
                if mod.enabled():
                    providers[p] = mod
    _providers = providers or None
    return providers
    
def expand_star(mod_name):
    """
    Expand something like 'jellyroll.providers.*' into a list of all the modules
    there.
    """
    expanded = []
    mod_dir = os.path.dirname(__import__(mod_name[:-2], {}, {}, ['']).__file__)
    for f in glob.glob1(mod_dir, "[!_]*.py"):
        expanded.append('%s.%s' % (mod_name[:-2], f[:-3]))
    return expanded
    
def update(providers, c = 0):
    """
    Update a given set of providers. If the list is empty, it means update all
    of 'em.
    """
    active = active_providers()
    if providers is None:
        providers = active.keys()
    else:
        providers = set(active.keys()).intersection(providers)
        
    for provider in providers:
        log.debug("Updating from provider %r", provider)
        try:
            mod = active[provider]
        except KeyError:
            log.error("Unknown provider: %r" % provider)
            continue

        log.info("Running '%s.update()'", provider)
        try:
            mod.update(c)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception, e:
            log.error("Failed during '%s.update()'", provider)
            log.exception(e)
            continue

        log.info("Done with provider %r", provider)
