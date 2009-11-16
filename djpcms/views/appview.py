import copy

from django import http
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, RequestContext
from django.utils.dates import MONTHS_3_REV

from djpcms.models import AppPage
from djpcms.utils.html import Paginator
from djpcms.views.baseview import djpcmsview
from djpcms.views.site import get_view_from_url


class AppView(djpcmsview):
    '''
    Base class for application views
    '''
    creation_counter = 0
    page_model       = AppPage
    
    def __init__(self,
                 regex  = None,
                 parent = None,
                 name   = None,
                 isapp  = True,
                 template_name = None,
                 in_navigation = False):
        # number of positional arguments in the url
        self.num_args = 0
        self.urlbit   = regex or u''
        self.parent   = parent
        self.name     = name
        self._regex   = ''
        self.isapp    = isapp
        self.func     = None
        self.appmodel = None
        self.code     = None
        self.editurl  = None
        self.in_navigation = in_navigation
        if template_name:
            self.template_name = template_name
        # Increase the creation counter, and save our local copy.
        self.creation_counter = AppView.creation_counter
        AppView.creation_counter += 1
        
    def __unicode__(self):
        return u'%s: %s' % (self.name,self.regex)
    
    def __get_regex(self):
        return '^%s$' % self._regex
    regex = property(fget = __get_regex)
    
    def __get_model(self):
        return self.appmodel.model
    model = property(fget = __get_model)
    
    def urlname(self, cl):
        if not self.breadcrumbs:
            if not cl.page:
                return self.appmodel.name
            else:
                return cl.page.href_name
        else:
            return ' '.join(self.breadcrumbs) % cl.urlargs
        
    def title(self, cl):
        if not cl.page:
            return self.appmodel.name
        else:
            return cl.page.title
    
    def edit_regex(self, edit):
        return r'^%s/%s$' % (edit,self._regex)
    
    def get_prefix(self, data):
        '''
        Get form prefix from data.
        '''
        for k,v in data.items():
            sv = str(v)
            if sv and k.endswith('-prefix'):
                return sv
    
    def processurlbits(self, appmodel):
        '''
        Process url bits and store information for navigation and urls
        '''
        self.appmodel = appmodel
        if self.parent:
            baseurl = self.parent._regex
            purl    = self.parent.purl
            nargs   = self.parent.num_args
        else:
            baseurl = self.appmodel.baseurl[1:]
            purl    = self.appmodel.baseurl
            nargs   = 0
        
        breadcrumbs = []
        if self.urlbit:
            bits = self.urlbit.split('/')
            for bit in bits:
                if bit:
                    if bit.startswith('('):
                        st = bit.find('<') + 1
                        en = bit.find('>')
                        if st and en:
                            name = bit[st:en]
                        else:
                            nargs += 1
                            name   = 'arg_no_key_%s' % nargs
                            
                        name  = '%(' + name + ')s'
                        purl += name + '/'
                        breadcrumbs.append(name)
                    else:
                        breadcrumbs.append(bit)
                        purl += '%s/' % bit
            self._regex = '%s%s/' % (baseurl,self.urlbit)
        else:
            self._regex = baseurl
        
        self.breadcrumbs = breadcrumbs
        self.purl     = purl
        self.num_args = nargs
        
    def content_dict(self, cl):
        return copy.copy(cl.urlargs)
        
    def get_url(self, request, **kwargs):
        '''
        get application url
        '''
        if kwargs:
            return self.purl % kwargs
        else:
            return self.purl
    
    def parentview(self, request):
        '''
        Retrive the parent view
        '''
        if not self.parent:
            # No parent check for flat pages
            return get_view_from_url(request,self.appmodel.parent_url)
        else:
            return self.parent
    
    def get_page(self):
        if self.code:
            try:
                return self.page_model.objects.get_for_code(self.code)
            except:
                if self.parent:
                    return self.parent.get_page()
                else:
                    return None
        else:
            return None
    
    def basequery(self, request, **kwargs):
        '''
        Base query for application
        If this is the root view (no parents) it returns the default
        basequery
        '''
        if self.parent:
            return self.parent.appquery(request)
        else:
            return self.appmodel.basequery(request)
    
    def appquery(self, request, *args, **kwargs):
        '''
        This function implements the application query.
        By default return the input basequery (usually all items of a model)
        @param request: HttpRequest
        @param *args: Extra positional arguments coming from the database
        @param *kwargs: Extra key-valued arguments coming from the database
        @return: a queryset
        '''
        return self.basequery(request)
    
    def render(self, request, prefix, wrapper, *args, **kwargs):
        '''
        Render the application child.
        This method is reimplemented by subclasses.
        By default it renders the search application
        '''
        pass
    
    def inner_content(self, request):
        return self.render(request,None,None)
    
    def __deepcopy__(self, memo):
        return copy.copy(self)


class SearchApp(AppView):
    '''
    Base class for searching objects in model
    '''
    def __init__(self, *args, **kwargs):
        super(SearchApp,self).__init__(*args,**kwargs)
    
    def get_item_template(self, obj):
        opts = obj._meta
        template_name_0 = '%s_search_item.html' % opts.module_name
        template_name_1 = '%s/%s' % (opts.app_label,template_name_0)
        return [template_name_0,template_name_1]
    
    def render(self, cl, prefix, wrapper, *args, **kwargs):
        '''
        Perform the custom query over the model objects and return a paginated result
        @param request: HttpRequest
        @param prefix: prefix for forms
        @param wrapper: html wrapper object
        @see: djpcms.utils.html.pagination for pagination
        '''
        request = cl.request
        kwargs.update(cl.kwargs)
        args  = cl.args + args
        cl    = self.requestview(request, *args, **kwargs)
        query = self.appquery(request, *cl.args, **cl.kwargs)
        f  = self.appmodel.get_searchform(request, prefix, wrapper, cl.get_url())
        p  = Paginator(request, query)
        c  = self.content_dict(cl)
        c.update({'form':f,
                  'paginator': p,
                  'items': self.data_generator(cl, prefix, wrapper, p.qs)})
        return loader.render_to_string(['bits/pagination.html',
                                        'djpcms/bits/pagination.html'],
                                        c)
    
    def data_generator(self, cl, prefix, wrapper, data):
        '''
        Return a generator for the query.
        This function can be overritten by derived classes
        '''
        request = cl.request
        app = self.appmodel
        for obj in data:
            content = app.object_content(request, prefix, wrapper, obj)
            content.update({'item': obj,
                            'editurl': app.editurl(request, obj),
                            'viewurl': app.viewurl(request, obj),
                            'deleteurl': app.deleteurl(request, obj)})
            yield loader.render_to_string(template_name    = self.get_item_template(obj),
                                          context_instance = RequestContext(request, content))


class ArchiveApp(SearchApp):
    '''
    Search view with archive subviews
    '''
    def __init__(self, *args, **kwargs):
        super(ArchiveApp,self).__init__(*args,**kwargs)
    
    def _date_code(self):
        return self.appmodel.date_code
    
    def content_dict(self, cl):
        c = super(ArchiveApp,self).content_dict(cl)
        month = c.get('month',None)
        if month:
            try:
                c['month'] = int(month)
            except:
                c['month'] = MONTHS_3_REV.get(month,None)
        year = c.get('year',None)
        day  = c.get('day',None)
        if year:
            c['year'] = int(year)
        if day:
            c['day'] = int(day)
        return c
    
    def appquery(self, request, year = None, month = None, day = None, **kwargs):
        dt       = self._date_code()
        dateargs = {}
        if year:
            dateargs['%s__year' % dt] = int(year)
        
        if month:
            try:
                month = int(month)
            except:
                month = MONTHS_3_REV.get(str(month),None)
            if month:
                dateargs['%s__month' % dt] = month
    
        if day:
            dateargs['%s__day' % dt] = int(day)
            
        qs = self.basequery(request, **kwargs)
        if dateargs:
            return qs.filter(**dateargs)
        else:
            return qs 
        
        

class AddApp(AppView):
    '''
    Standard Add method
    '''
    def __init__(self, regex = 'add', parent = None,
                 name = 'add', isapp = True, **kwargs):
        '''
        Set some default values for add application
        '''
        super(AddApp,self).__init__(regex  = regex,
                                    parent = parent,
                                    name   = name,
                                    isapp  = isapp,
                                    **kwargs)
    
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
        
        
# Application views which requires an object
class ObjectView(AppView):
    '''
    Application view for objects.
    A view of this type has an embedded object available.
    URL is generated by the object
    '''
    def __init__(self, *args, **kwargs):
        super(ObjectView,self).__init__(*args, **kwargs)
    
    def get_url(self, request, instance = None, **urlargs):
        '''
        get object application url
        '''
        if instance:
            return self.purl % self.appmodel.objectbits(instance)
        else:
            return self.purl % urlargs
    
    def title(self, request, pagetitle):
        try:
            return pagetitle % self.object
        except:
            return pagetitle
    

# View and object
class ViewApp(ObjectView):
    
    def __init__(self, regex = '(\d+)', parent = None, name = 'view', **kwargs):
        '''
        By default the relative url is given by the databse id number
        '''
        super(ViewApp,self).__init__(regex = regex, parent = parent,
                                     name = name, **kwargs)
        
    def render(self, request, prefix, wrapper, *args):
        '''
        Render the add view
        '''
        return self.appmodel.render_object(request, prefix, wrapper, self.object)
    
    
# Delete an object. POST method only. not GET method should modify databse
class DeleteApp(ObjectView):
    _methods      = ('post',) 
    def __init__(self, regex = 'delete', parent = 'view', name = 'delete', **kwargs):
        super(DeleteApp,self).__init__(regex = regex, parent = parent, name = name, **kwargs)
      

# Edit/Change an object
class EditApp(ObjectView):
    '''
    Edit view
    '''
    def __init__(self, regex = 'edit', parent = 'view', name = 'edit',  **kwargs):
        super(EditApp,self).__init__(regex = regex, parent = parent, name = name, **kwargs)
    
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