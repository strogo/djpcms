from djpcms.models import Page, Site

from .orms import model_to_dict



def create_page(parent = None, user = None, inner_template = None, commit = True, **kwargs):
    data = model_to_dict(Page)
    

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
    if pages:
        return pages[0]


def get_for_application(djp, code):
    '''Obtain a Page from an application code'''
    site = get_current_site(djp)    
    pages = Page.objects.filter(site = site, application_view = code)
    return pages