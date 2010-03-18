from django.contrib.admin import site, autodiscover
from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.contrib.admin import ModelAdmin, HORIZONTAL, VERTICAL
from django.contrib.admin import StackedInline, TabularInline
from django.contrib.admin import AdminSite, site, import_module

from djpcms.conf import settings


_old_render_change_form = ModelAdmin.render_change_form
def new_render_change_form(self, request, context, **kwargs):
    context['cssajax'] = settings.HTML_CLASSES
    return _old_render_change_form(self, request, context, **kwargs)


#Inject! because Python is cool
ModelAdmin.render_change_form = new_render_change_form

 