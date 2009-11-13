import copy

from django.http import Http404

from djpcms.views.appview import AppView, ObjectView, SearchApp
from djpcms.views.site import get_view_from_url
from djpcms.html import htmlPlugin
    
        
class DeleteApp(ObjectView):
    def __init__(self, url = 'delete', parent = 'view', **kwargs):
        super(DeleteApp,self).__init__(url, parent, **kwargs)
        

class ViewApp(ObjectView):
    
    def __init__(self, url, parent = None, **kwargs):
        super(ViewApp,self).__init__(url, parent, **kwargs)
        
    def render(self, request, prefix, wrapper, *args):
        '''
        Render the add view
        '''
        return self.appmodel.render_object(request, prefix, wrapper, self.object)
        

class EditApp(ObjectView):
    '''
    Edit view
    '''
    def __init__(self, url = 'edit', parent = 'view', **kwargs):
        super(EditApp,self).__init__(url, parent, **kwargs)
    
    def render(self, request, prefix, wrapper, *args):
        '''
        Render the edit view
        '''
        url = self.get_url(request, *args)
        f = self.appmodel.get_form(request, prefix, wrapper, url, instance = self.object)
        return f.render()
    
    def default_ajax_view(self, request):
        prefix = self.get_prefix(dict(request.POST.items()))
        f = self.appmodel.get_form(request, prefix = prefix, instance = self.object)
        if f.is_valid():
            try:
                instance = f.save()
            except Exception, e:
                return f.errorpost('%s' % e)
            return f.messagepost('%s modified' % instance)
        else:
            return f.jerrors    

class AddApp(AppView):
    '''
    Standard Add method
    '''
    def __init__(self, isapp = True):
        super(AddApp,self).__init__('add',None,'add_item',isapp = isapp)
    
    def render(self, request, prefix, wrapper, *args):
        '''
        Render the add view
        '''
        url = self.get_url(request, *args)
        f = self.appmodel.get_form(request, prefix, wrapper, url)
        return f.render()
    
    def default_ajax_view(self, request):
        prefix = self.get_prefix(dict(request.POST.items()))
        f = self.appmodel.get_form(request, prefix = prefix)
        if f.is_valid():
            try:
                instance = f.save()
            except Exception, e:
                return f.errorpost('%s' % e)
            return f.messagepost('%s added' % instance)
        else:
            return f.jerrors       
    

class ArchiveidApp(AppView):
    '''
    Search view with archive subviews
    '''
    def __init__(self, *args, **kwargs):
        super(ArchiveidApp,self).__init__(*args,**kwargs)
    
    def render(self, request, prefix, wrapper, *args):
        '''
        Render the application child.
        This method is reimplemented by subclasses.
        By default it renders the search application
        '''
        url  = self.get_url(*args)
        data = self.appmodel.get_archive(*args).order_by('-%s' % self.appmodel.date_code)
        return self.appmodel.paginate(request, data)


class TagApp(SearchApp):
    
    def __init__(self, *args, **kwargs):
        self.tags = None
        super(TagApp,self).__init__(*args,**kwargs)
    
    def title(self, request):
        return self.breadcrumbs()

    def handle_reponse_arguments(self, request, *args, **kwargs):
        view = copy.copy(self)
        view.args = args
        return view
        
    def myquery(self, query, request, *tags):
        return self.model.objects.with_all(tags, queryset = query)

