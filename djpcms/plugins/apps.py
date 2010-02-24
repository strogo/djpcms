from django import forms
from django.contrib.contenttypes.models import ContentType
from django.template import loader

from tagging.forms import TagField

from djpcms.plugins import DJPplugin
from djpcms.forms import SearchForm


 


class LatestItemForm(forms.Form):
    for_model   = forms.ModelChoiceField(queryset = ContentType.objects.all(), empty_label=None)
    max_display = forms.IntegerField(initial = 10)
    pagination  = forms.BooleanField(initial = False, required = False)
    tags        = TagField(required = False)
    
    def clean_for_model(self):
        from djpcms.views import appsite
        ct = self.cleaned_data['for_model']
        model = ct.model_class()
        appmodel = appsite.site.for_model(model)
        if appmodel:
            return ct
        else:
            raise forms.ValidationError('Model %s has no application installed' % ct)



class SearchModelForm(forms.Form):
    for_model   = forms.ModelChoiceField(queryset = ContentType.objects.all(), empty_label=None)
    title       = forms.CharField(required = False, max_length = 50)


class SearchBox(DJPplugin):
    '''
    A search box for a model
    '''
    name = 'search-box'
    description = 'Search a Django Model'
    form = SearchModelForm
    
    def render(self, djp, wrapper, prefix, for_model = None, title = None, **kwargs):
        from djpcms.views import appsite
        if for_model:
            ct = ContentType.objects.get(id = int(for_model))
            model = ct.model_class()
            appmodel = appsite.site.for_model(model)
            if appmodel:
                search_url = appmodel.searchurl(djp.request)
                if search_url:
                    f = SearchForm(data = djp.request.GET)
                    return loader.render_to_string(['search_form.html',
                                                    'djpcms/form/search_form.html'],
                                                    {'html':  f,
                                                     'title': title or 'Enter your search term',
                                                     'url':   search_url,
                                                     'method':'get'})




class LatestItems(DJPplugin):
    name = 'latest-items'
    description   = 'Latest items for a model'
    form          = LatestItemForm
    template_name = ['bits/object_list.html',
                     'djpcms/bits/object_list.html']
    
    def datagen(self, appmodel, djp, wrapper, items):
        for obj in items:
            content = appmodel.object_content(djp, obj)
            yield loader.render_to_string(appmodel.get_item_template(obj, wrapper),
                                          content)
            
    def render(self, djp, wrapper, prefix,
               for_model = None, max_display = 5,
               pagination = False, tags = '', **kwargs):
        from djpcms.views import appsite
        try:
            ct = ContentType.objects.get(id = for_model)
            model = ct.model_class()
            appmodel = appsite.site.for_model(model)
            if not appmodel:
                return u''
        except:
            return u''
        data = appmodel.basequery(djp.request)
        max_display = max(max_display,1)
        items = data[0:max_display]
        if not items:
            return u''
        content = {'items': self.datagen(appmodel, djp, wrapper, items)}
        return loader.render_to_string(self.template_name, content)
    