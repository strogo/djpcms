'''
Requires django-tagging
'''
from django.template import RequestContext, loader

from tagging.models import TaggedItem
from tagging.utils import calculate_cloud

from djpcms.views.customview import CustomView
from djpcms.views.apps.appurls import ModelApplication, ArchiveApplication
from djpcms.views.appview import AppView, ArchiveApp, TagApp, SearchApp



class tagcloud(CustomView):
    verbose_name = "Tag Cloud for a Model"
    
    def get_tags(self, tag1 = None, tag2 = None, tag3 = None, **kwargs):
        if tag1:
            if tag2:
                if tag3:
                    return (tag1,tag2,tag3)
                else:
                    return (tag1,tag2)
            else:
                return tag1,
            
    def render(self, request, cl, prefix, wrapper,
               formodel = None, steps = 4, min_count = None, **kwargs):
        steps     = int(steps)
        if min_count:
            min_count = int(min_count)
        appmodel  = appsite.site.for_model(formodel)
        
        tags = self.get_tags(**kwargs)
        if tags:
            query = TaggedItem.objects.get_by_model(formodel,tags)
            query = self.model.objects.usage_for_queryset(query, counts=True)
            tags  = calculate_cloud(query)
        else:
            tags = self.model.objects.cloud_for_model(formodel,
                                                      steps = steps,
                                                      min_count = min_count)
        for tag in tags:
            tag.url = appmodel.tagurl(request, tag.name)
            if tag.count == 1:
                tag.times = 'time'
            else:
                tag.times = 'times'
        c = self.content_dict(cl)
        c['tags'] = tags
        return loader.render_to_string(['bits/tag_cloud.html',
                                        'djpcms/bits/tag_cloud.html'],
                                        RequestContext(request, c))


class CloudApp(AppView):
    '''
    Application to display a tag cloud
    '''
    def __init__(self, *args, **kwargs):
        self.steps     = kwargs.pop('steps',4)
        self.min_count = kwargs.pop('min_count',None)
        self.formodel  = kwargs.pop('formodel',None)
        super(CloudApp,self).__init__(*args, **kwargs)
    
    def render(self, cl, prefix, wrapper, *args, **kwargs):
        '''
        Render a tag cloud
        '''
        request   = cl.request
        formodel  = self.appmodel.formodel
        args      = cl.args or args
        steps     = int(kwargs.get('steps',self.steps))
        min_count = kwargs.get('min_count',self.min_count)
        if min_count:
            min_count = int(min_count)
            
        if args:
            query = TaggedItem.objects.get_by_model(formodel,args)
            query = self.model.objects.usage_for_queryset(query, counts=True)
            tags  = calculate_cloud(query)
        else:
            tags = self.model.objects.cloud_for_model(formodel,
                                                      steps = steps,
                                                      min_count = min_count)
        for tag in tags:
            tag.url = self.appmodel.tagurl(request, tag.name)
            if tag.count == 1:
                tag.times = 'time'
            else:
                tag.times = 'times'
        c = self.content_dict(cl)
        c['tags'] = tags
        return loader.render_to_string(['bits/tag_cloud.html',
                                        'djpcms/bits/tag_cloud.html'],
                                        RequestContext(request, c))
        
class TagArchiveApp(ArchiveApp):
    
    def __init__(self, *args, **kwargs):
        super(TagArchiveApp,self).__init__(*args, **kwargs)
        
    def appquery(self, request, year = None, month = None, day = None, **tags):
        query = super(TagArchiveApp,self).appquery(request, year = year, month = month, day = day)
        if tags:
            return TaggedItem.objects.get_by_model(query, tags.values())
        else:
            return query


class ArchiveTaggedApplication(ArchiveApplication):
    '''
    Comprehensive Tagged Archive Application urls
    '''
    search         =    ArchiveApp(in_navigation = True)
    year_archive   =    ArchiveApp(regex = '(?P<year>\d{4})',
                                   parent = 'search')
    month_archive  =    ArchiveApp(regex = '(?P<month>\w{3})',
                                   parent = 'year_archive')
    day_archive    =    ArchiveApp(regex = '(?P<day>\d{2})',
                                   parent = 'month_archive')
    tag1           = TagArchiveApp(regex = 'tags/(?P<tag1>\w+)',
                                   parent = 'search')
    year_archive1  = TagArchiveApp(regex = '(?P<year>\d{4})',
                                   parent = 'tag1')
    month_archive1 = TagArchiveApp(regex = '(?P<month>\w{3})',
                                   parent = 'year_archive')
    day_archive1   = TagArchiveApp(regex = '(?P<day>\d{2})',
                                   parent = 'month_archive')
    tag2           = TagArchiveApp(regex = 'tags2/(?P<tag1>\w+)/(?P<tag2>\w+)',
                                   parent = 'search')
    year_archive2  = TagArchiveApp(regex = '(?P<year>\d{4})',
                                   parent = 'tag2')
    month_archive2 = TagArchiveApp(regex = '(?P<month>\w{3})',
                                   parent = 'year_archive2')
    day_archive2   = TagArchiveApp(regex = '(?P<day>\d{2})',
                                   parent = 'month_archive2')
    tag3           = TagArchiveApp(regex = 'tags3/(?P<tag1>\w+)/(?P<tag2>\w+)/(?P<tag3>\w+)',
                                   parent = 'search')
    year_archive3  = TagArchiveApp(regex = '(?P<year>\d{4})',
                                   parent = 'tag3')
    month_archive3 = TagArchiveApp(regex = '(?P<month>\w{3})',
                                   parent = 'year_archive3')
    day_archive3   = TagArchiveApp(regex = '(?P<day>\d{2})',
                                   parent = 'month_archive3')
    
    def basequery(self, request):
        return self.formodel.objects.all()
    
    def tagurl(self, request, tag):
        view = self.getapp('tag')
        if view:
            return view.requestview(request, tag = tag).get_url()
    
    def object_content(self, request, prefix, wrapper, obj):
        tagurls = []
        tagview = self.getapp('tag')
        if obj.tags and tagview:
            tags = obj.tags.split(u' ')
            for tag in tags:
                tagurls.append({'url':tagview.get_url(request, tag = tag),'name':tag})
        return {'tagurls': tagurls}
    
    
    