'''
Requires django-tagging

Battery included plugins and application for tagging and tagging with archive
'''
from django import forms
from django.template import RequestContext, loader
from django.contrib.contenttypes.models import ContentType

from tagging.models import TaggedItem
from tagging.utils import calculate_cloud, LOGARITHMIC, LINEAR

from djpcms.plugins.base import DJPplugin
from djpcms.views import appsite
from djpcms.views.appview import AppView, ArchiveView
from djpcms.utils import form_kwargs


class CloudForm(forms.Form):
    for_model = forms.ModelChoiceField(queryset = ContentType.objects.all(), empty_label=None)
    steps     = forms.IntegerField(initial = 4)
    min_count = forms.IntegerField(initial = 0)
    type      = forms.ChoiceField(choices = ((LOGARITHMIC,"LOGARITHMIC"),(LINEAR,"LINEAR")), initial = LOGARITHMIC)


class tagcloud(DJPplugin):
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
            
    def get_form(self, djp):
        return CloudForm(**form_kwargs(request = djp.request))
    
    def __call__(self, djp, formodel = None, steps = 4, min_count = None, **kwargs):
        if not formodel:
            return u''
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

       
class TagArchiveView(ArchiveView):
    
    def __init__(self, *args, **kwargs):
        super(TagArchiveView,self).__init__(*args, **kwargs)
        
    def appquery(self, request, year = None, month = None, day = None, **tags):
        query = super(TagArchiveView,self).appquery(request, year = year, month = month, day = day)
        if tags:
            return TaggedItem.objects.get_by_model(query, tags.values())
        else:
            return query


class ArchiveTaggedApplication(appsite.ArchiveApplication):
    '''
    Comprehensive Tagged Archive Application urls
    '''
    search         =    ArchiveView(in_navigation = True)
    year_archive   =    ArchiveView(regex = '(?P<year>\d{4})',
                                    parent = 'search')
    month_archive  =    ArchiveView(regex = '(?P<month>\w{3})',
                                    parent = 'year_archive')
    day_archive    =    ArchiveView(regex = '(?P<day>\d{2})',
                                    parent = 'month_archive')
    tag1           = TagArchiveView(regex = 'tags/(?P<tag1>\w+)',
                                    parent = 'search')
    year_archive1  = TagArchiveView(regex = '(?P<year>\d{4})',
                                    parent = 'tag1')
    month_archive1 = TagArchiveView(regex = '(?P<month>\w{3})',
                                    parent = 'year_archive')
    day_archive1   = TagArchiveView(regex = '(?P<day>\d{2})',
                                    parent = 'month_archive')
    tag2           = TagArchiveView(regex = 'tags2/(?P<tag1>\w+)/(?P<tag2>\w+)',
                                    parent = 'search')
    year_archive2  = TagArchiveView(regex = '(?P<year>\d{4})',
                                    parent = 'tag2')
    month_archive2 = TagArchiveView(regex = '(?P<month>\w{3})',
                                    parent = 'year_archive2')
    day_archive2   = TagArchiveView(regex = '(?P<day>\d{2})',
                                    parent = 'month_archive2')
    tag3           = TagArchiveView(regex = 'tags3/(?P<tag1>\w+)/(?P<tag2>\w+)/(?P<tag3>\w+)',
                                    parent = 'search')
    year_archive3  = TagArchiveView(regex = '(?P<year>\d{4})',
                                    parent = 'tag3')
    month_archive3 = TagArchiveView(regex = '(?P<month>\w{3})',
                                    parent = 'year_archive3')
    day_archive3   = TagArchiveView(regex = '(?P<day>\d{2})',
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
    
    
    