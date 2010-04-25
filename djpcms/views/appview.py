import operator
import copy
from datetime import datetime

from django import http
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, RequestContext
from django.utils.dateformat import format
from django.utils.text import smart_split
from django.contrib import messages
from django.utils.translation import ugettext as _

from djpcms.conf import settings
from djpcms.utils.html import Paginator
from djpcms.utils.func import force_number_insert
from djpcms.utils.ajax import jremove, dialog, jredirect
from djpcms.utils import form_kwargs, force_unicode, construct_search, isexact

from djpcms.views.regex import RegExUrl 
from djpcms.views.cache import pagecache
from djpcms.views.baseview import djpcmsview


class pageinfo(object):
    
    def __init__(self,url,last_modified):
        self.url = url
        self.last_modified = last_modified


class AppViewBase(djpcmsview):
    
    def __init__(self,
                 name   = None,
                 parent = None,
                 regex = None,
                 splitregex = False,
                 insitemap = True):
        self.__page    = None
        self.name      = name
        self.parent    = parent
        self.appmodel  = None
        self.insitemap = insitemap
        self.urlbit    = RegExUrl(regex,splitregex)
        self.regex     = None
        
    def __get_baseurl(self):
        return self.appmodel.baseurl
    baseurl = property(__get_baseurl)
        
    def set_page(self, page):
        self.__page = page
        
    def get_page(self):
        if self.__page:
            return self.__page
        else:
            try:
                self.__page = pagecache.get_for_application(self.code)
                return self.__page
            except:
                if self.parent:
                    return self.parent.get_page()
    
    def has_permission(self, request = None, obj = None):
        '''
        Delegate to appmodel
        '''
        return self.appmodel.has_permission(request, obj)
    
    def render(self, djp, **kwargs):
        '''
        Render the application child.
        This method is reimplemented by subclasses.
        By default it renders the search application
        '''
        pass
    
    


class AppView(AppViewBase):
    '''
    Base class for application views
    '''
    creation_counter = 0
    
    def __init__(self,
                 regex     = None,
                 parent    = None,
                 name      = None,
                 isapp     = True,
                 isplugin  = False,
                 template_name = None,
                 in_navigation = False,
                 insitemap  = True,
                 splitregex = True):
        AppViewBase.__init__(self,
                             name = name,
                             regex = regex,
                             splitregex = splitregex,
                             parent = parent,
                             insitemap = insitemap)
        self.isapp    = isapp
        self.isplugin = isplugin
        self.func     = None
        self.code     = None
        self.editurl  = None
        self.in_nav   = in_navigation
        if template_name:
            self.template_name = template_name
        # Increase the creation counter, and save our local copy.
        self.creation_counter = AppView.creation_counter
        AppView.creation_counter += 1
    
    def get_media(self):
        return self.appmodel.media
    
    def isroot(self):
        return self.appmodel.root_application is self
    
    def __unicode__(self):
        return u'%s: %s' % (self.name,self.regex)
    
    def __get_model(self):
        return self.appmodel.model
    model = property(fget = __get_model)
    
    def in_navigation(self, request, page):
        if self.in_nav:
            if page:
                return page.in_navigation
            else:
                return 1
        else:
            return 0
    
    def linkname(self, djp):
        page = djp.page
        if not page:
            return self.appmodel.name
        else:
            return page.link
        
    def title(self, page, **urlargs):
        if not page:
            return self.appmodel.name
        else:
            return page.title
    
    def edit_regex(self, edit):
        baseurl = self.baseurl
        if baseurl:
            return r'^%s/%s%s$' % (edit,baseurl[1:],self.regex)
        else:
            return None
    
    def processurlbits(self, appmodel):
        '''
        Process url bits and store information for navigation and urls
        '''
        self.appmodel = appmodel
        self.ajax     = appmodel.ajax
        if self.parent:
            self.regex = self.parent.regex + self.urlbit
        else:
            self.regex = self.urlbit
        
    def content_dict(self, cl):
        return copy.copy(cl.urlargs)
        
    def get_url(self, request, **kwargs):
        purl = self.regex.get_url(request, **kwargs)
        return '%s%s' % (self.baseurl,purl)
    
    def parentresponse(self, djp):
        '''
        Retrive the parent response
        '''
        return self.appmodel.parentresponse(djp, self)
    
    def modelparent(self):
        '''
        Return a parent with same model if it exists
        '''
        p = self.parent
        if p:
            if getattr(p,'model',None) == self.model:
                return p
        return None
    
    def basequery(self, request, **kwargs):
        '''
        Base query for application
        If this is the root view (no parents) it returns the default
        basequery
        '''
        if self.modelparent():
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
    
    def get_prefix(self, djp):
        return None
        data = dict(djp.request.POST.items())
        for k,v in data.items():
            sv = str(v)
            if sv and k.endswith('-prefix'):
                return sv
    
    def permissionDenied(self, djp):
        return self.appmodel.permissionDenied(djp)
    
    def sitemapchildren(self):
        return []
    
    def __deepcopy__(self, memo):
        return copy.copy(self)   
    
    
    
class SearchView(AppView):
    search_text = 'search_text'
    '''
    Base class for searching objects in model
    '''
    def __init__(self, *args, **kwargs):
        super(SearchView,self).__init__(*args,**kwargs)
    
    def appquery(self, request, *args, **kwargs):
        '''
        This function implements the application query.
        By default return the input basequery (usually all items of a model)
        @param request: HttpRequest
        @param *args: Extra positional arguments coming from the database
        @param *kwargs: Extra key-valued arguments coming from the database
        @return: a queryset
        '''
        qs = self.basequery(request)
        
        slist = self.appmodel.get_search_fields()
        if request.method == 'GET':
            data = dict(request.GET.items())
        else:
            data = dict(request.POST.items())
        search_string = data.get(self.search_text,None)
        if slist and search_string:
            bits  = smart_split(search_string)
            #bits  = search_string.split(' ')
            for bit in bits:
                bit = isexact(bit)
                if not bit:
                    continue
                or_queries = [Q(**{construct_search(field_name): bit}) for field_name in slist]
                other_qs   = QuerySet(self.model)
                other_qs.dup_select_related(qs)
                other_qs   = other_qs.filter(reduce(operator.or_, or_queries))
                qs         = qs & other_qs    
        return qs
    
    def render(self, djp, **kwargs):
        '''
        Perform the custom query over the model objects and return a paginated result
        @param request: HttpRequest
        @param prefix: prefix for forms
        @param wrapper: html wrapper object
        @see: djpcms.utils.html.pagination for pagination
        '''
        request  = djp.request
        appmodel = self.appmodel
        if kwargs:
            urlargs = djp.urlargs
            urlargs.update(kwargs)
            djp = self(request, *urlargs)
        query   = self.appquery(request, *djp.args, **djp.kwargs)
        f  = self.appmodel.get_searchform(djp)
        p  = Paginator(request, query)
        c  = self.content_dict(djp)
        c.update({'paginator': p,
                  'djp': djp,
                  'url': djp.url,
                  'model': self.model,
                  'css': appmodel.ajax,
                  'headers': appmodel.list_display})
        if p.qs:
            c['items'] = self.appmodel.data_generator(djp, p.qs)
            
        return loader.render_to_string(['components/pagination.html',
                                        'djpcms/components/pagination.html'],
                                        c)


class ArchiveView(SearchView):
    '''
    Search view with archive subviews
    '''
    def __init__(self, *args, **kwargs):
        super(ArchiveView,self).__init__(*args,**kwargs)
    
    def _date_code(self):
        return self.appmodel.date_code
    
    def content_dict(self, djp):
        c = super(ArchiveView,self).content_dict(djp)
        month = c.get('month',None)
        if month:
            c['month'] = self.appmodel.get_month_number(month)
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
            month = self.appmodel.get_month_number(month)
            if month:
                dateargs['%s__month' % dt] = month
    
        if day:
            dateargs['%s__day' % dt] = int(day)
            
        qs = self.basequery(request, **kwargs)
        if dateargs:
            return qs.filter(**dateargs)
        else:
            return qs

class DayArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(DayArchiveView,self).__init__(*args,**kwargs)
    def title(self, page, **urlargs):
        return urlargs.get('day',None)
    
class MonthArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(MonthArchiveView,self).__init__(*args,**kwargs)
    def title(self, page, **urlargs):
        return urlargs.get('month',None)
    
class YearArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(YearArchiveView,self).__init__(*args,**kwargs)
    def title(self, page, **urlargs):
        return urlargs.get('year',None)
    
    
def render_form(form, djp):
    djp.media += form.media
    helper = getattr(form,'helper',None)
    if helper:
        return helper.render(form)
    else:
        return form.render()
    
def saveform(self, djp, editing = False):
    view       = djp.view
    request    = djp.request
    is_ajax    = request.is_ajax()
    djp.prefix = self.get_prefix(djp)
    cont       = request.POST.has_key("_save_and_continue")
    url        = djp.url
    next       = None
    
    if request.POST.has_key("_cancel"):
        redirect_url = next
        if not redirect_url:
            if djp.instance:
                redirect_url = view.appmodel.viewurl(request,djp.instance)
            if not redirect_url:
                redirect_url = view.appmodel.searchurl(request) or '/'

        if is_ajax:
            return jredirect(url = redirect_url)                
        else:
            return http.HttpResponseRedirect(redirect_url)
    
    f = self.get_form(djp)
    helper = getattr(f,'helper',f)
    if f.is_valid():
        try:
            mch        = 'added'
            if editing:
                mch = 'changed'
            instance = self.save(f)
            dt = datetime.now()
            c = {'name': force_unicode(instance._meta.verbose_name),
                 'obj': instance,
                 'dt': format(dt,settings.DATETIME_FORMAT),
                 'mch': mch}
            msg = _('The %(name)s "%(obj)s" was succesfully %(mch)s %(dt)s') % c
            messages.info(request, msg)
        except Exception, e:
            if is_ajax:
                return helper.json_form_error(f,e)
            else:
                return self.handle_response(djp)
        
        if cont:
            redirect_url = view.appmodel.editurl(request,instance)
        else:
            redirect_url = next
            if not next:
                redirect_url = view.appmodel.viewurl(request,instance)
            
        if is_ajax:
            return jredirect(url = redirect_url)                
        else:
            return http.HttpResponseRedirect(redirect_url)
    else:
        if is_ajax:
            return helper.json_errors(f)
        else:
            return self.handle_response(djp)
        

class AddView(AppView):
    '''
    Standard Add method
    '''
    def __init__(self, regex = 'add', parent = None,
                 name = 'add', isplugin = True, in_navigation = True, form = None,
                 **kwargs):
        '''
        Set some default values for add application
        '''
        super(AddView,self).__init__(regex  = regex,
                                     parent = parent,
                                     name   = name,
                                     isplugin = isplugin,
                                     in_navigation = in_navigation,
                                     **kwargs)
        self._form = form
    
    def has_permission(self, request = None, obj = None):
        return self.appmodel.has_add_permission(request, obj)
    
    def get_form(self, djp):
        return self.appmodel.get_form(djp, form = self._form)
    
    def save(self, f):
        return self.appmodel.object_from_form(f)
    
    def render(self, djp, **kwargs):
        '''
        Render the add view
        '''
        f = self.get_form(djp)
        return render_form(f,djp)
    
    def default_post(self, djp):
        '''
        Add new model instance
        '''
        return saveform(self,djp)
    
        
        
# Application views which requires an object
class ObjectView(AppView):
    '''
    Application view for objects.
    A view of this type has an embedded object available.
    URL is generated by the object
    '''
    def __init__(self, *args, **kwargs):
        super(ObjectView,self).__init__(*args, **kwargs)
    
    def get_url(self, djp, instance = None, **urlargs):
        '''
        get object application url
        If instance not defined it return None
        '''
        if instance:
            urlargs = self.appmodel.objectbits(instance)
        else:
            instance = self.appmodel.get_object(**urlargs)
        
        if not instance:
            raise http.Http404
        
        djp.instance = instance
        return super(ObjectView,self).get_url(djp, **urlargs)
    
    
    def title(self, page, instance = None, **urlargs):
        return self.appmodel.title_object(instance)
    

class ViewView(ObjectView):
    '''
    Home page for an object
    '''
    def __init__(self, regex = '(\d+)', parent = None, name = 'view', **kwargs):
        '''
        By default the relative url is given by the databse id number
        '''
        super(ViewView,self).__init__(regex = regex, parent = parent,
                                      name = name, **kwargs)
    
    def linkname(self, djp):
        return str(djp.instance)
        
    def render(self, djp):
        '''
        Render the add view
        '''
        return self.appmodel.render_object(djp)
    
    def sitemapchildren(self):
        return self.appmodel.sitemapchildren(self)    
    
    
# Delete an object. POST method only. not GET method should modify databse
class DeleteView(ObjectView):
    _methods      = ('post',) 
    
    def __init__(self, regex = 'delete', parent = 'view', name = 'delete',
                 isapp = False, **kwargs):
        super(DeleteView,self).__init__(regex = regex, parent = parent,
                                        name = name, isapp = isapp,
                                        **kwargs)
        
    def has_permission(self, request = None, obj = None):
        return self.appmodel.has_delete_permission(request, obj)
    
    def default_post(self, djp):
        instance = djp.instance
        try:
            bid = self.appmodel.remove_object(instance)
            if bid:
                return jremove('#%s' % bid)
            else:
                pass
        except Exception, e:
            raise ValueError('Could not remove %s: %s' % (instance,e))
      

# Edit/Change an object
class EditView(ObjectView):
    '''
    Edit view
    '''
    def __init__(self, regex = 'edit', parent = 'view', name = 'edit',  **kwargs):
        super(EditView,self).__init__(regex = regex, parent = parent, name = name, **kwargs)
    
    def has_permission(self, request = None, obj = None):
        return self.appmodel.has_edit_permission(request, obj)
    
    def get_form(self, djp):
        return self.appmodel.get_form(djp)
    
    def render(self, djp):
        f = self.get_form(djp)
        return render_form(f,djp)
    
    def save(self, f):
        return self.appmodel.object_from_form(f)
    
    def ajax__save(self, djp):
        '''
        Save and redirect to default redirect
        '''
        return self.default_post(djp,True)
    
    def ajax__save_and_continue(self, djp):
        '''
        Save and redirect to default redirect
        '''
        return self.default_post(djp,False)
    
    def default_post(self, djp):
        return saveform(self,djp,True)

    def defaultredirect(self, djp):
        return self.appmodel.viewurl(djp.request, djp.instance) or djp.url