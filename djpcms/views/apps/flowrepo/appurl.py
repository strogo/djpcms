#
# djpcms application for django-flowrepo
#
#@requires: django-flowrepo
#@see: yet to be released. Do not used it in production
#
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory
from django import http

from flowrepo.models import FlowItem
from flowrepo.forms import FlowItemForm

from djpcms.views import appview
from djpcms.views import appsite
from djpcms.views.apps.tagging import tagurl
from djpcms.utils.html import form, formlet
from djpcms.utils import form_kwargs


class ContentView(appview.SearchView):
    
    def __init__(self, *args, **kwargs):
        super(ContentView,self).__init__(*args,**kwargs)
    
    def appquery(self, request, content = None, **kwargs):
        qs = self.basequery(request, **kwargs)
        if content:
            cmodels  = self.appmodel.content_models
            contents = content.split('+')
            ids      = []
            for content in contents:
                model = cmodels.get(content,None)
                if model:
                    ctype = ContentType.objects.get_for_model(model)
                    ids.append(ctype.id)
            if ids:
                return qs.filter(content_type__pk__in = ids)
            else:
                return self.model.objects.none()
        raise self.model.objects.none()
    
       
class FlowRepoApplication(tagurl.ArchiveTaggedApplication):
    '''
    Base application class for flowitem models
    '''
    date_code        = 'timestamp'
    form_withrequest = True
    form             = FlowItemForm
    split_days       = True
    inherit          = True
    insitemap        = True
    content_names    = {}   # dictionary for mapping a model into a name used for url
    
    def __init__(self, *args, **kwargs):
        super(FlowRepoApplication,self).__init__(*args, **kwargs)
        content_models = {}
        for cn,model in FlowItem.objects.models_by_name.items():
            cname = self.content_names.get(model,None)
            if not cname:
                cname = cn
                self.content_names[model] = cname
            content_models[cname] = model
        self.content_models = content_models

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
        c['authors']  = obj.niceauthors()
        c['external'] = True
        return c
    
    def objectbits(self, obj):
        '''
        Get arguments from model instance used to construct url
        By default it is the object id
        @param obj: instance of self.model
        @return: dictionary of url bits 
        '''
        obj = obj.object
        rep = {'content':self.content_names[obj.__class__]}
        if hasattr(obj,'slug'):
            rep['id'] = obj.slug
        else:
            rep['id'] = obj.id
        return rep
    
    def get_object(self, *args, **kwargs):
        '''
        Retrive an instance of self.model for arguments.
        By default arguments is the object id,
        Reimplement for custom arguments
        '''
        try:
            cn = kwargs.get('content')
            model = self.content_models.get(cn,None)
            if model:
                id   = kwargs.get('id',None)
                try:
                    obj = model.objects.get(slug = id)
                except:
                    try:
                        obj = model.objects.get(id = int(id))
                    except:
                        return None
            return FlowItem.objects.get_from_instance(obj)
        except:
            return None
        
            
    def get_form(self, djp, prefix = None, initial = None, wrapped = True):
        instance   = djp.instance
        request    = djp.request
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




class FlowModelApplication(FlowRepoApplication):
    inherit  = True
    
    add      = appview.AddView(regex = 'write')
    edit     = appview.EditView(regex = '(?P<id>[-\.\w/]+)', parent = 'add', splitregex = False)
    view     = appview.ViewView(regex = '(?P<id>[-\.\w/]+)', splitregex = False)
    #edit     = appview.EditView(regex = 'edit', parent = 'view')
    
    def objectbits(self, object):
        '''
        Get arguments from model instance used to construct url
        By default it is the object id
        @param obj: instance of self.model
        @return: dictionary of url bits 
        '''
        try:
            obj = object.object
        except:
            obj = object
        if hasattr(obj,'slug'):
            parent = getattr(obj,'parent',None)
            if parent:
                bits = '%s/%s' % (self.objectbits(parent)['id'],obj.slug)
            else:
                bits = obj.slug
            return {'id': bits}
        else:
            return {'id': obj.id}
    
    def get_object(self, *args, **kwargs):
        '''
        Retrive an instance of self.model for arguments.
        By default arguments is the object id,
        Reimplement for custom arguments
        '''
        try:
            id   = kwargs.get('id',None)
            try:
                slug = id.split('/')[-1]
                obj = self.model.objects.get(slug = slug)
            except:
                try:
                    obj = self.model.objects.get(id = int(id))
                except:
                    return None
            return FlowItem.objects.get_from_instance(obj)
        except:
            return None