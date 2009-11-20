'''
Requires django-tagging

Battery included plugins and application for tagging and tagging with archive
'''
from djpcms.views import appsite
from djpcms.views.appview import AppView, ArchiveView, SearchView

from tagging.models import TaggedItem


class TagView(SearchView):
    
    def __init__(self, *args, **kwargs):
        super(TagView,self).__init__(*args, **kwargs)
        
    def appquery(self, request, **tags):
        qs = self.basequery(request)
        if tags:
            return TaggedItem.objects.get_by_model(qs, tags.values())
        else:
            return qs


class TagArchiveView(ArchiveView):
    
    def __init__(self, *args, **kwargs):
        super(TagArchiveView,self).__init__(*args, **kwargs)
        
    def appquery(self, request, year = None, month = None, day = None, **tags):
        query = super(TagArchiveView,self).appquery(request, year = year, month = month, day = day)
        if tags:
            return TaggedItem.objects.get_by_model(query, tags.values())
        else:
            return query


class TagApplication(appsite.ModelApplication):
    search  = SearchView(in_navigation = True)
    cloud   = SearchView(regex = 'tag', parent = 'search')
    tag     = TagView(regex = '(?P<tag1>\w+)', parent = 'cloud')
    

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
    
    def tagurl(self, request, *tags):
        view = self.getapp('tag%s' % len(tags))
        if view:
            kwargs = {}
            c = 1
            for tag in tags:
                kwargs['tag%s' % c] = tag
                c += 1
            return view.requestview(request, **kwargs).url
    
    def object_content(self, request, prefix, wrapper, obj):
        tagurls = []
        tagview = self.getapp('tag1')
        if obj.tags and tagview:
            tags = obj.tags.split(u' ')
            for tag in tags:
                djp = tagview.requestview(request, tag1 = tag)
                tagurls.append({'url':djp.url,
                                'name':tag})
        return {'tagurls': tagurls}
    
    
    