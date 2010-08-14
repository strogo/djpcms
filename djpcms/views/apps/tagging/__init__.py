'''
Requires django-tagging

Battery included plugins and application for tagging and tagging with archive
'''
from django.utils.http import urlquote
from djpcms.views import appsite
from djpcms.views import appview
from djpcms.views.apps import archive

from tagging.models import TaggedItem

# REGEX FOR A TAG
tag_regex = '[-\.\+\#\'\:\w]+'


class TagView(appview.SearchView):
    
    def __init__(self, *args, **kwargs):
        super(TagView,self).__init__(*args, **kwargs)
    
    def title(self, page, **urlargs):
        return urlargs.get('tag1','')
    
    def appquery(self, request, **tags):
        qs = self.basequery(request)
        if tags:
            return TaggedItem.objects.get_by_model(qs, tags.values())
        else:
            return qs


class TagArchiveView(appview.ArchiveView):
    
    def __init__(self, *args, **kwargs):
        super(TagArchiveView,self).__init__(*args, **kwargs)
    
    def title(self, page, **urlargs):
        return urlargs.get('tag1','')
    
    def linkname(self, djp):
        urlargs = djp.urlargs
        return urlargs.get('tag1',None)
        
    def appquery(self, request, year = None, month = None, day = None, **tags):
        query = super(TagArchiveView,self).appquery(request, year = year, month = month, day = day)
        if tags:
            return TaggedItem.objects.get_by_model(query, tags.values())
        else:
            return query



def add_tags(self, c, djp, obj):
    request = djp.request
    tagurls = []
    tagview = self.getapp('tag1')
    if obj.tags and tagview:
        tags = obj.tags.split(u' ')
        for tag in tags:
            djp = tagview(request, tag1 = tag)
            tagurls.append({'url':djp.url,
                            'name':tag})
    c['tagurls'] = tagurls
    return c

def tagurl(self, request, *tags):
    view = self.getapp('tag%s' % len(tags))
    if view:
        kwargs = {}
        c = 1
        for tag in tags:
            #tag = urlquote(tag)
            kwargs['tag%s' % c] = tag
            c += 1
        return view(request, **kwargs).url



class TagApplication(appsite.ModelApplication):
    search  = appview.SearchView(in_navigation = True)
    cloud   = appview.SearchView(regex = 'tags', parent = 'search', in_navigation = True)
    tag1    = TagView(regex = '(?P<tag1>%s)' % tag_regex, parent = 'cloud')
    
    def tagurl(self, request, *tags):
        return tagurl(self, request, *tags)
        
    def object_content(self, djp, obj):
        c = super(TagApplication,self).object_content(djp, obj)
        return add_tags(self, c, djp, obj)



class ArchiveTaggedApplication(archive.ArchiveApplication):
    '''
    Comprehensive Tagged Archive Application urls
    '''
    search        = appview.ArchiveView(in_navigation = True)
    year_archive  = appview.YearArchiveView(regex = '(?P<year>\d{4})')
    month_archive = appview.MonthArchiveView(regex = '(?P<month>\w{3})', parent = 'year_archive')
    day_archive   = appview.DayArchiveView(regex = '(?P<day>\d{2})',   parent = 'month_archive')
    
    tagc0          = appview.AppView(regex = 'tags', in_navigation = True)
    tag1           = TagArchiveView(regex = '(?P<tag1>%s)' % tag_regex, parent = 'tagc0')
    year_archive1  = TagArchiveView(regex = '(?P<year>\d{4})',  parent = 'tag1')
    month_archive1 = TagArchiveView(regex = '(?P<month>\w{3})', parent = 'year_archive1')
    day_archive1   = TagArchiveView(regex = '(?P<day>\d{2})',   parent = 'month_archive1')
    
    tagc1          = appview.AppView(regex = 'tags2/(?P<tag1>%s)' % tag_regex)
    tag2           = TagArchiveView(regex = '(?P<tag2>%s)' % tag_regex, parent = 'tagc1')
    year_archive2  = TagArchiveView(regex = '(?P<year>\d{4})',  parent = 'tag2')
    month_archive2 = TagArchiveView(regex = '(?P<month>\w{3})', parent = 'year_archive2')
    day_archive2   = TagArchiveView(regex = '(?P<day>\d{2})',   parent = 'month_archive2')
    
    def tagurl(self, request, *tags):
        return tagurl(self, request, *tags)
    
    def object_content(self, djp, obj):
        c = super(ArchiveTaggedApplication,self).object_content(djp, obj)
        return add_tags(self, c, djp, obj)
    
    
    