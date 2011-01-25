from djpcms import sites
from djpcms.models import Page, Site
from djpcms.forms import cms, ValidationError

from .orms import mapper, getid


def all():
    return mapper(Page).all()


def create_page(parent = None, user = None,
                inner_template = None, commit = True,
                **kwargs):
    '''Create a new page.'''
    if parent:
        data = mapper(Page).model_to_dict(Page)
        data.update(**kwargs)
        if not user:
            user = parent.user
        if not inner_template:
            inner_template = parent.inner_template
        parent = parent.id
        data.update({'parent':parent,
                     'user':getid(user),
                     'inner_template': getid(inner_template),
                     'site':getid(get_current_site())})
    else:
        data = {'site':get_current_site()}
        
    f = cms.PageForm(data = data, parent = parent, model = Page)
    if f.is_valid():
        if commit:
            return f.save(commit = commit)
        else:
            return f
    else:
        raise ValidationError(' '.join(f.errors))


def get_current_site(request = None):
    if request:
        site_id = request.site.settings.SITE_ID
    else:
        site_id = sites.settings.SITE_ID
    try:
        return mapper(Site).get(id = site_id)
    except:
        if not mapper(Site).all() and site_id == 1:
            site = Site(name = 'example.com', domain = 'example.com')
            site.save()
        return site
    
    
def get_root(request):
    site = get_current_site(request)
    pages = mapper(Page).filter(site = site, parent = None)
    if pages:
        return pages[0]


def get_for_application(djp, code):
    '''Obtain a Page from an application code'''
    site = get_current_site(djp)    
    pages = mapper(Page).filter(site = site, application_view = code)
    return pages
