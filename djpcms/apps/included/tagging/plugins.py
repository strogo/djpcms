#
# Collection of plugins which handle tags
#
from djpcms import forms, get_site
from djpcms.template import loader
from djpcms.plugins import DJPplugin

from django.contrib.contenttypes.models import ContentType

from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud, LOGARITHMIC, LINEAR


class CloudForm(forms.Form):
    for_model = forms.ModelChoiceField(queryset = ContentType.objects.all(), empty_label=None)
    steps     = forms.IntegerField(initial = 4)
    min_count = forms.IntegerField(initial = 0)
    type      = forms.ChoiceField(choices = ((LOGARITHMIC,"LOGARITHMIC"),(LINEAR,"LINEAR")), initial = LOGARITHMIC)


class tagcloud(DJPplugin):
    name        = "tag-cloud"
    description = "Tag Cloud for a Model"
    form        = CloudForm
    
    def get_tags(self, tag1 = None, tag2 = None, tag3 = None, **kwargs):
        if tag1:
            if tag2:
                if tag3:
                    return (tag1,tag2,tag3)
                else:
                    return (tag1,tag2)
            else:
                return tag1,
    
    def render(self, djp, wrapper, prefix,
               for_model = None, steps = 4, min_count = None, **kwargs):
        try:
            formodel = ContentType.objects.get(id = int(for_model)).model_class()
        except:
            return u''
        
        steps     = int(steps)
        if min_count:
            min_count = int(min_count)
        site = get_site(djp.request.path)
        appmodel  = site.for_model(formodel)
        
        tags = self.get_tags(**kwargs)
        if tags:
            query = TaggedItem.objects.get_by_model(formodel,tags)
            query = self.model.objects.usage_for_queryset(query, counts=True)
            tags  = calculate_cloud(query)
        else:
            tags = Tag.objects.cloud_for_model(formodel,
                                               steps = steps,
                                               min_count = min_count)
        request = djp.request
        for tag in tags:
            try:
                tag.url = appmodel.tagurl(request, tag.name)
            except:
                tag.url = None
            if tag.count == 1:
                tag.times = 'time'
            else:
                tag.times = 'times'
        c = {'tags': tags}
        return loader.render_to_string(['bits/tag_cloud.html',
                                        'djpcms/bits/tag_cloud.html'],c)


class TagForObject(DJPplugin):
    name        = "object-tags"
    description = "Tags for an object"
    
    def render(self, djp, wrapper, prefix, **kwargs):
        request = djp.request
        try:
            appmodel = djp.view.appmodel
            tags = djp.instance.tags
            if tags:
                tagnames = tags.split(' ')
                tags = []
                for name in tagnames:
                    tag = {'name': name}
                    try:
                        tag['url'] = appmodel.tagurl(request, name)
                    except:
                        tag['url'] = None
                    tags.append(tag)
                c = {'tags': tags,
                     'instance': djp.instance}
                return loader.render_to_string(['bits/object_tags.html',
                                                'djpcms/bits/object_tags.html'],c)
            else:
                return u''
        except:
            return u''