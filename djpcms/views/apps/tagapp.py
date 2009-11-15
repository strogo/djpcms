from django.template import RequestContext, loader

from tagging.models import TaggedItem
from tagging.utils import calculate_cloud

from djpcms.views.appview import AppView, ArchiveApp


class CloudApp(AppView):
    
    def __init__(self, *args, **kwargs):
        self.steps     = kwargs.pop('steps',4)
        self.min_count = kwargs.pop('min_count',None)
        self.formodel  = kwargs.pop('formodel',None)
        super(CloudApp,self).__init__(*args, **kwargs)
    
    def render(self, request, prefix, wrapper, *args, **kwargs):
        '''
        Render a tag cloud
        '''
        args      = self.args or args
        steps     = int(kwargs.get('steps',self.steps))
        min_count = kwargs.get('min_count',self.min_count)
        if min_count:
            min_count = int(min_count)
        if args and args[0]:
            query = TaggedItem.objects.get_by_model(self.formodel,args)
            query = self.model.objects.usage_for_queryset(query, counts=True)
            tags  = calculate_cloud(query)
        else:
            tags = self.model.objects.cloud_for_model(self.formodel,
                                                      steps = steps,
                                                      min_count = min_count)
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
        
class TagArchiveApp(ArchiveApp):
    
    def __init__(self, *args, **kwargs):
        self.formodel = kwargs.pop('formodel',None)
        super(TagArchiveApp,self).__init__(*args, **kwargs)
        
    def basequery(self, request):
        return self.formodel.objects.all()
    
    def myquery(self, query, request, *tags, **kwargs):
        '''
        Here we assume the args tuple are tags, while kwargs contains
        date infomation (year,month,day) as in the Archive application
        '''
        query = super(TagArchiveApp,self).myquery(query, request, **kwargs)
        return TaggedItem.objects.get_by_model(query, *tags)

