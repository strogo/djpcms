#
# djpcms application for django-flowrepo
#
#@requires: django-flowrepo
#@see: yet to be released. Do not used it in production
#

from flowrepo.settings import FLOWREPO_SLUG_UNIQUE

from djpcms.views import appview
from djpcms.views.apps import tagapp


class BaseBlogBlogApplication(tagapp.ArchiveTaggedApplication):
    date_code = 'published'
    inherit   = True
    
    def basequery(self, request):
        return self.model.objects.basequery(user = request.user)
    
    def has_permission(self, request = None, obj=None):
        if not obj:
            return True
        if not request:
            return obj.can_user_view()
        else:
            return obj.can_user_view(request.user)
    
    def object_content(self, djp, obj):
        '''
        Utility function for getting more content out of an instance of a model
        '''
        c = super(BaseBlogBlogApplication,self).object_content(djp,obj)
        c['authors'] = obj.niceauthors()
        return c
    


class BlogApplication(BaseBlogBlogApplication):
    '''
    Writing application
    @note: this application assume FLOWREPO_UNIQUE_SLUG is set to True in the settings file.
           In this way the slug field of a Report is used to build the url
    '''
    inherit   = True  
    
    add       = appview.AddView(regex = 'add', parent = 'search', isplugin = False)
    view      = appview.ViewView(regex = 'item/(?P<slug>[\w-]+)', parent = 'search')
    edit      = appview.EditView(regex = 'edit/(?P<slug>[\w-]+)', parent = 'search')
    
    def objectbits(self, obj):
        '''
        Get arguments from model instance used to construct url
        By default it is the object id
        @param obj: instance of self.model
        @return: dictionary of url bits 
        '''
        return {'slug': obj.slug}
    
    def get_object(self, *args, **kwargs):
        '''
        Retrive an instance of self.model for arguments.
        By default arguments is the object id,
        Reimplement for custom arguments
        '''
        try:
            slug = kwargs.get('slug',None)
            return self.model.objects.get(slug = slug)
        except:
            return None
        