#
# djpcms application for django-flowrepo
#
#@requires: django-flowrepo
#@see: yet to be released. Do not used it in production
#
from django.forms.models import modelform_factory

from flowrepo.settings import FLOWREPO_SLUG_UNIQUE
from flowrepo.models import FlowItem
from flowrepo.forms import ReportForm, get_flow_form

from djpcms.views import appview
from djpcms.views import appsite
from djpcms.views.apps.tagging import tagurl
from djpcms.utils.html import form, formlet
from djpcms.utils import form_kwargs


class FlowRepoApplication(tagapp.ArchiveTaggedApplication):
    '''
    Base application class for flowitem models
    '''
    date_code        = 'timestamp'
    form_withrequest = True
    form             = get_flow_form
    split_days       = True
    inherit          = True
    insitemap        = True

    def basequery(self, request):
        return FlowItem.objects.public(user = request.user, model = self.model)

    def has_permission(self, request = None, obj=None):
        if not obj:
            return True
        if not obj:
            return False
        if not request:
            return obj.can_user_view()
        else:
            return obj.can_user_view(request.user)
        
    def get_object_view_template(self, obj, wrapper):
        item = obj
        obj  = obj.object
        opts = obj._meta
        template_name = '%s.html' % opts.module_name
        return ['components/%s' % template_name,
                '%s/%s' % (opts.app_label,template_name),
                'djpcms/components/object.html']
        
    def get_item_template(self, obj, wrapper):
        model = obj.content_type.model
        return ['components/%s_list_item.html' % model,
                'flowrepo/%s_list_item.html' % model,
                'flowrepo/flowitem_list_item.html']
    
    def object_content(self, djp, obj):
        '''
        Utility function for getting more content out of an instance of a model
        '''
        c = super(FlowRepoApplication,self).object_content(djp,obj)
        c['authors'] = obj.niceauthors()
        return c


class CategoryApplication(appsite.ModelApplication):
    category = appview.AppView(in_navigation = True)
    view = appview.ViewView(regex = '(?P<category>%s)' % tagapp.tag_regex, parent = 'category')
    
    def objectbits(self, obj):
        return {'category': obj.slug}
    
    def get_object(self, *args, **kwargs):
        '''
        Retrive an instance of self.model for arguments.
        By default arguments is the object id,
        Reimplement for custom arguments
        '''
        try:
            slug = kwargs.get('category',None)
            return self.model.objects.get(slug = slug)
        except:
            return None
    
    

class BlogApplication(FlowRepoApplication):
    '''
    Writing application
    @note: this application assume FLOWREPO_UNIQUE_SLUG is set to True in the settings file.
           In this way the slug field of a Report is used to build the url
    '''
    inherit   = True
    date_code = 'timestamp'
    form      = ReportForm
    
    add       = appview.AddView(regex = 'write',
                                parent = 'search',
                                isplugin = False,
                                in_navigation = True)
    view      = appview.ViewView(regex = '(?P<slug>[\w-]+)', parent = 'search')
    edit      = appview.EditView(regex = 'edit', parent = 'view')
    
    def objectbits(self, obj):
        '''
        Get arguments from model instance used to construct url
        By default it is the object id
        @param obj: instance of self.model
        @return: dictionary of url bits 
        '''
        obj = obj.object
        if FLOWREPO_SLUG_UNIQUE:
            return {'slug': obj.slug}
        else:
            return {'slug': obj.slug}
    
    def get_object(self, *args, **kwargs):
        '''
        Retrive an instance of self.model for arguments.
        By default arguments is the object id,
        Reimplement for custom arguments
        '''
        try:
            if FLOWREPO_SLUG_UNIQUE:
                slug = kwargs.get('slug',None)
                obj = self.model.objects.get(slug = slug)
            else:
                slug = kwargs.get('slug',None)
                obj = self.model.objects.get(slug = slug)
            return FlowItem.objects.get_from_instance(obj)
        except:
            return None
        
    def get_form(self, djp, prefix = None, initial = None, wrapped = True):
        instance = djp.instance
        request  = djp.request
        mform      = modelform_factory(self.model, self.form)
        mform.user = request.user
        initial    = self.update_initial(request, mform, initial)
        f     = mform(**form_kwargs(request     = request,
                                    initial     = initial,
                                    instance    = instance,
                                    prefix      = prefix,
                                    withrequest = self.form_withrequest))
        rf          = form(url = djp.url, template = 'djpcms/flowrepo/editform.html')
        rf['form']  = formlet(f,
                              submit = self.submit(instance),
                              template = 'djpcms/flowrepo/editrepo.html')
        if self.form_ajax:
            rf.addClass(self.ajax.ajax)
        return rf