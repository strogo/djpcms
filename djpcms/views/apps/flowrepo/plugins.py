# Requires flowrepo (not yet released)
#
from django.template import loader

from djpcms.plugins import DJPplugin
from djpcms.utils.html import htmlwrap

from flowrepo.models import FlowRelated, FlowItem, Report

class YourDraft(DJPplugin):
    name = 'flowrepo-draft'
    description = 'User private items'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        from djpcms.views import appsite
        request = djp.request
        qs = FlowItem.objects.private(request.user)
        if not qs:
            return None
        return loader.render_to_string(['report_draft_list.html',
                                        'flowrepo/report_draft_list.html'],
                                        {'items': self.paginator(appmodel,djp,qs)})
        
    def paginator(self, appmodel, djp, qs):
        for obj in qs:
            content = appmodel.object_content(djp, obj)
            yield loader.render_to_string(['report_list_item.html',
                                           'flowrepo/report_list_item.html'],
                                           content)
            

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