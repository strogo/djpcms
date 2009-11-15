'''
Requires django-tagging
'''
from django.template import RequestContext, loader

from tagging.models import TaggedItem
from tagging.utils import calculate_cloud

from djpcms.views.apps.appurls import ModelApplication, ArchiveApplication
from djpcms.views.appview import AppView, ArchiveApp, TagApp, SearchApp


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
        super(TagArchiveApp,self).__init__(*args, **kwargs)
        
    def myquery(self, query, request, *tags, **kwargs):
        '''
        Here we assume the args tuple are tags, while kwargs contains
        date infomation (year,month,day) as in the Archive application
        '''
        query = super(TagArchiveApp,self).myquery(query, request, **kwargs)
        return TaggedItem.objects.get_by_model(query, *tags)


class ArchiveTaggedApplication(ArchiveApplication):
    '''
    An archive Tagged application
    '''
    formodel      = None
    cloud         = CloudApp(in_navigation = True)
    tag           = TagApp(regex = '(\w+)', parent = 'cloud')
    year_archive  = TagArchiveApp(regex = '(?P<year>\d{4})',  parent = 'tag')
    month_archive = TagArchiveApp(regex = '(?P<month>\w{3})', parent = 'year_archive', in_navigation = False)
    day_archive   = TagArchiveApp(regex = '(?P<day>\d{2})',   parent = 'month_archive', in_navigation = False)
    
    def basequery(self, request):
        return self.formodel.objects.all()
    
    def tagurl(self, request, tag):
        view = self.getapp('tag')
        if view:
            view = view.handle_reponse_arguments(request,tag)
            return view.get_url()
    
    def object_content(self, request, prefix, wrapper, obj):
        tagurls = []
        tagview = self.getapp('tag')
        if obj.tags and tagview:
            tags = obj.tags.split(u' ')
            for tag in tags:
                tagurls.append({'url':tagview.get_url(tag),'name':tag})
        return {'tagurls': tagurls}
    
    
    
    
class TaggedApplication(ModelApplication):
    search         = SearchApp()
    tags1          = TagApp('tags1/(\w+)', in_navigation = False)
    tags2          = TagApp('tags2/(\w+)/(\w+)', in_navigation = False)
    tags3          = TagApp('tags3/(\w+)/(\w+)/(\w+)', in_navigation = False)
    tags4          = TagApp('tags4/(\w+)/(\w+)/(\w+)/(\w+)', in_navigation = False)
    
    def tagurl(self, request, *tags):
        N = len(tags)
        view = self.getapp('tags%s' % N)
        if view:
            return view.get_url(*tags)    
    
    def object_content(self, request, prefix, wrapper, obj):
        tagurls = []
        tagview = self.getapp('tags1')
        if obj.tags and tagview:
            tags = obj.tags.split(u' ')
            for tag in tags:
                tagurls.append({'url':tagview.get_url(tag),'name':tag})
        return {'tagurls': tagurls}