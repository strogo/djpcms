from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory

from djpcms.template import loader
from djpcms.conf import settings
from djpcms.plugins import DJPplugin
from djpcms.utils.uniforms import UniForm, FormLayout, Fieldset
from djpcms.utils.html import submit
from djpcms.forms.cms import SearchForm
from djpcms.views import appsite


def registered_models():
    ids = []
    for model,app in appsite.site._registry.items():
        if isinstance(app,appsite.ModelApplication) and not app.hidden:
            try:
                ct = ContentType.objects.get_for_model(model)
            except:
                continue
            ids.append(ct.id)
    return ContentType.objects.filter(pk__in = ids)


def app_model_from_ct(ct):
    if ct:
        try:
            ct = ContentType.objects.get(id = int(ct))
        except:
            if settings.DEBUG:
                return u'Content type %s not available' % ct, False
            else:
                return u'', False
        model = ct.model_class()
        appmodel = appsite.site.for_model(model)
        if appmodel:
            return appmodel, True
        else:
            return u'', False
    else:
        return u'', False
    

class ForModelForm(forms.Form):
    for_model   = forms.ModelChoiceField(queryset = registered_models(), empty_label=None)
    
    def clean_for_model(self):
        ct = self.cleaned_data['for_model']
        model = ct.model_class()
        appmodel = appsite.site.for_model(model)
        if appmodel:
            return ct
        else:
            raise forms.ValidationError('Model %s has no application installed' % ct)


class LatestItemForm(ForModelForm):
    max_display = forms.IntegerField(initial = 10)
    pagination  = forms.BooleanField(initial = False, required = False)


class FormModelForm(ForModelForm):
    method      = forms.ChoiceField(choices = (('get','get'),('post','post')))
    ajax        = forms.BooleanField(initial = False, required = False)


class SearchModelForm(FormModelForm):
    title       = forms.CharField(required = False, max_length = 50)


class FilterModelForm(FormModelForm):
    pass


class SearchBox(DJPplugin):
    '''
    A search box for a model
    '''
    name = 'search-box'
    description = 'Search a Django Model'
    form = SearchModelForm
    
    def render(self, djp, wrapper, prefix, for_model = None, title = None, **kwargs):
        if for_model:
            try:
                ct = ContentType.objects.get(id = int(for_model))
            except:
                if settings.DEBUG:
                    return 'Content type %s not available' % for_model
                else:
                    return ''
            model = ct.model_class()
            appmodel = appsite.site.for_model(model)
            if appmodel:
                search_url = appmodel.searchurl(djp.request)
                if search_url:
                    f = SearchForm(data = djp.request.GET)
                    return loader.render_to_string(['search_form.html',
                                                    'bits/search_form.html',
                                                    'djpcms/bits/search_form.html'],
                                                    {'html':  f,
                                                     'title': title or 'Enter your search term',
                                                     'url':   search_url,
                                                     'method':'get'})


class ModelFilter(DJPplugin):
    '''Display filters for a model registered in the application registry.'''
    name = 'model-filter'
    description = 'Filter a model'
    form = FilterModelForm
    
    def render(self, djp, wrapper, prefix, for_model = None,
               ajax = False, method = 'get', **kwargs):
        appmodel, ok = app_model_from_ct(for_model)
        if not ok:
            return appmodel
        filters = appmodel.search_fields
        if not filters:
            return u''
        request = djp.request
        search_url = appmodel.searchurl(request)
        if not search_url:
            return u''
        model = appmodel.model
        initial = dict((request.GET or request.POST).items())
        form = modelform_factory(model, appmodel.form, fields = filters, exclude = [])
        form.layout = FormLayout()
        f = UniForm(form(initial = initial),
                    method = method,
                    action = search_url)
        if ajax:
            f.addClass(djp.css.ajax)
        f.inputs.append(submit(value = 'filter', name = '_filter'))
        return f.render()
    
    
class ModelLinksForm(forms.Form):
    asbuttons = forms.BooleanField(initial = True, required = False, label = 'as buttons')
    layout = forms.ChoiceField(choices = (('horizontal','horizontal'),('vertical','vertical')))
    exclude = forms.CharField(max_length=600,required=False)
    
    
class ObjectLinks(DJPplugin):
    name = 'edit-object'
    description = 'Links for a model instance'
    form = ModelLinksForm
    def render(self, djp, wrapper, prefix, layout = 'horizontal',
               asbuttons = True, exclude = '', **kwargs):
        try:
            exclude = exclude.split(',')
            links = djp.view.appmodel.object_links(djp,djp.instance, asbuttons=asbuttons, exclude=exclude)
            links['layout'] = layout
            return loader.render_to_string(['bits/editlinks.html',
                                            'djpcms/bits/editlinks.html'],
                                            links)
        except:
            return u''
    
    
class ModelLinks(DJPplugin):
    name = 'model-links'
    description = 'Links for a model'
    form = ModelLinksForm
    def render(self, djp, wrapper, prefix, layout = 'horizontal',
               asbuttons = True, exclude = '', **kwargs):
        try:
            exclude = exclude.split(',')
            links = djp.view.appmodel.links(djp, asbuttons=asbuttons, exclude=exclude)
            links['layout'] = layout
            return loader.render_to_string(['bits/editlinks.html',
                                            'djpcms/bits/editlinks.html'],
                                            links)
        except:
            return u''
            

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
               pagination = False, **kwargs):
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
    