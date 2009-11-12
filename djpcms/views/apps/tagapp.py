from django.template import RequestContext, loader

from tagging.models import TaggedItem
from tagging.utils import calculate_cloud

from djpcms.plugins.application import appsite
from djpcms.views.appview import AppView


class CloudApp(AppView):
    
    def __init__(self, *args, **kwargs):
        self.formodel = kwargs.pop('formodel',None)
        super(CloudApp,self).__init__(*args, **kwargs)
    
    def render(self, request, prefix, wrapper, *args):
        '''
        Render a tag cloud
        '''
        args = self.args or args
        if args and args[0]:
            qs   = TaggedItem.objects.get_by_model(self.formodel,args)
            tags = self.model.objects.usage_for_queryset(qs, counts=True)
            tags = calculate_cloud(tags)
        else:
            tags = self.model.objects.cloud_for_model(self.formodel)
        for tag in tags:
            tag.url = self.appmodel.tagurl(request,tag.name)
            if tag.count == 1:
                tag.times = 'time'
            else:
                tag.times = 'times'
        c = {'tags': tags}
        return loader.render_to_string(['content/tag_cloud.html',
                                        'djpcms/content/tag_cloud.html'],
                                        RequestContext(request, c))
        

