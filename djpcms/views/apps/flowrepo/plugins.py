# Requires flowrepo (not yet released)
#
from django.template import loader

from djpcms.plugins import DJPplugin

from flowrepo.models import Report

class YourDraft(DJPplugin):
    name = 'flowrepo-draft'
    description = 'User report drafts'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        from djpcms.views import appsite
        request = djp.request
        appmodel = appsite.site.for_model(Report)
        if not appmodel:
            return None
        qs = Report.objects.get_author_drafts(request.user)
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
        