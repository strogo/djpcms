# Requires flowrepo (not yet released)
#
from django.template import loader

from djpcms.plugins import DJPplugin
from djpcms.utils.html import htmlwrap
from djpcms.views.apps.flowrepo.forms import ChangeCategory

from flowrepo.models import FlowRelated, FlowItem, Report, Message, Category

class YourDraft(DJPplugin):
    name = 'flowrepo-draft'
    description = 'Private reports'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        request = djp.request
        qs = FlowItem.objects.private(request.user, Report)
        if not qs:
            return None
        return loader.render_to_string(['report_draft_list.html',
                                        'flowrepo/report_draft_list.html'],
                                        {'items': self.paginator(djp,qs)})
        
    def paginator(self, djp, qs):
        from djpcms.views import appsite
        for_model = appsite.site.for_model
        for obj in qs:
            object = obj.object
            if not object:
                continue
            appmodel = for_model(object.__class__)
            if appmodel:
                content  = appmodel.object_content(djp, obj)
                yield loader.render_to_string(['report_list_item.html',
                                               'flowrepo/report_list_item.html'],
                                               content)
            
class TwitterLine(DJPplugin):
    items = 5
    name = 'twitter-timeline'
    description = 'Twitter time-line'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        request = djp.request
        qs = FlowItem.objects.public(request.user, Message)
        if not qs:
            return None
        qs = qs[:self.items]
        return loader.render_to_string(['message_list.html',
                                        'djpcms/components/object_list.html'],
                                        {'items': self.paginator(djp,qs)})
        
    def paginator(self, djp, qs):
        from djpcms.views import appsite
        for_model = appsite.site.for_model
        appmodel = appsite.site.for_model(FlowItem)
        for obj in qs:
            if appmodel:
                content  = appmodel.object_content(djp, obj)
                yield loader.render_to_string(['message_list_item.html',
                                               'flowrepo/message_list_item.html'],
                                               content)

class CategoryLinks(DJPplugin):
    name = 'category-links'
    description = "Display links for a category"
    form          = ChangeCategory
    
    def render(self, djp, wrapper, prefix, category_name = None, **kwargs):
        if category_name:
            qs = Category.objects.filter(type__id = int(category_name))
        else:
            return u''
        if not qs:
            return u''
        return loader.render_to_string(['category_list.html',
                                        'components/category_list.html',
                                        'flowrepo/category_list.html'],
                                        {'items': self.paginator(djp,qs)})
    
    def paginator(self, djp, qs):
        from djpcms.views import appsite
        appmodel = appsite.site.for_model(Category)
        for obj in qs:
            if appmodel:
                content  = appmodel.object_content(djp, obj)
                yield loader.render_to_string(['category_list_item.html',
                                               'components/category_list_item.html',
                                               'flowrepo/category_list_item.html'],
                                               content)
        
    def edit_form(self, djp, category_name = None, **kwargs):
        if category_name:
            return EditContentForm(**form_kwargs(request = djp.request,
                                                 initial = {'category_name': category_name},
                                                 withrequest = True))


class LinkedItems(DJPplugin):
    '''
    Very very useful plugin for displaying a list of linked item
    to the flowitem object
    '''
    name = 'flowrepo-linked'
    description = "Linked item urls"
    
    def render(self, djp, wrapper, prefix, **kwargs):
        from djpcms.views import appsite
        instance = djp.instance
        if not isinstance(instance,FlowItem):
            return
        qs = FlowRelated.objects.filter(item = instance)
        if not qs:
            return
        request = djp.request
        return loader.render_to_string(['report_draft_list.html',
                                        'flowrepo/report_draft_list.html'],
                                        {'items': self.paginator(djp,qs)})
        
    def paginator(self, djp, qs):
        for obj in qs:
            object  = obj.object
            url     = object.url
            link    = htmlwrap('a', object.name)
            link._attrs['title'] = object.name
            link._attrs['href'] = url
            if not url.startswith('/'):
                link._attrs['target'] = "_blank"
            yield link.render()


class AddLinkedItems(DJPplugin):
    name = 'flowrepo-add-linked'
    description = "Add Linked item urls"
    
    def render(self, djp, wrapper, prefix, **kwargs):
        from djpcms.views import appsite
        instance = djp.instance
        if not isinstance(instance,FlowItem):
            return
        qs = FlowRelated.objects.filter(item = instance)
        if not qs:
            return
        request = djp.request
        return loader.render_to_string(['report_draft_list.html',
                                        'flowrepo/report_draft_list.html'],
                                        {'items': self.paginator(djp,qs)})
