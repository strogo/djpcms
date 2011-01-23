from djpcms import sites

if sites.settings.CMS_ORM == 'django':
    
    from djpcms.core.cmsmodels._django import *
    
elif sites.settings.CMS_ORM == 'stdnet':
    
    from djpcms.core.cmsmodels._stdnet import *
    
else:
    
    raise NotImplementedError('Objecr Relational Mapper {0} not available for CMS models'.format(settings.CMS_ORM))


def get_current_site(request):
    site_id = request.site.settings.SITE_ID
    try:
        return Site.objects.get(id = site_id)
    except:
        if not Site.objects.all() and site_id == 1:
            site = Site(name = 'example.com', domain = 'example.com')
            site.save()
        return site
    
    
def get_root(request):
    site = get_current_site(request)
    pages = Page.objects.filter(site = site, parent = None)
    if not pages:
        return pages[0]


def get_for_application(djp, code):
    '''Obtain a Page from an application code'''
    site = get_current_site(djp)    
    pages = Page.objects.filter(site = site, application_view = code)
    return pages