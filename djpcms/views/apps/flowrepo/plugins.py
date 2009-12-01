# Requires flowrepo (not yet released)
#
from django.template import loader

from djpcms.plugins import DJPplugin

from flowrepo.models import FlowItem, Report

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
        