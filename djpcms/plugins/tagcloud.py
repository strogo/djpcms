#
#    Requires tagging
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.template import loader

from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud, LOGARITHMIC, LINEAR

from djpcms.plugins import DJPplugin
from djpcms.views import appsite


class CloudForm(forms.Form):
    for_model = forms.ModelChoiceField(queryset = ContentType.objects.all(), empty_label=None)
    steps     = forms.IntegerField(initial = 4)
    min_count = forms.IntegerField(initial = 0)
    type      = forms.ChoiceField(choices = ((LOGARITHMIC,"LOGARITHMIC"),(LINEAR,"LINEAR")), initial = LOGARITHMIC)


class tagcloud(DJPplugin):
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
    
    def render(self, djp, for_model = None, steps = 4, min_count = None, **kwargs):
        try:
            formodel = ContentType.objects.get(id = int(for_model)).model_class()
        except:
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

