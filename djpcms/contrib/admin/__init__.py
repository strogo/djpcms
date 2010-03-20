from django.contrib.admin import site, autodiscover
from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.contrib.admin import ModelAdmin, HORIZONTAL, VERTICAL
from django.contrib.admin import StackedInline, TabularInline
from django.contrib.admin import AdminSite, site, import_module

from djpcms.views.cache import pagecache
from djpcms.utils.html import grid960
from djpcms.conf import settings
from djpcms.utils.navigation import Navigator


# Aijack admin site to inject some specific djpcms stuff

def _add_to_context(request, context):
    try:
        view = pagecache.view_from_url(request, '/')
        nav  = Navigator(view(request))
    except:
        nav = None
    context = context or {}
    context.update({'admin_site': True,
                    'cssajax': settings.HTML_CLASSES,
                    'grid':    grid960(),
                    'sitenav': nav})
    return context


_old_render_change_form = ModelAdmin.render_change_form
_old_changelist_view    = ModelAdmin.changelist_view
_old_index              = site.index
_old_app_index          = site.app_index

def new_render_change_form(self, request, context, **kwargs):
    return _old_render_change_form(self, request, _add_to_context(request, context), **kwargs)
def new_changelist_view(self, request, extra_context=None):
    return _old_changelist_view(self, request, _add_to_context(request, extra_context))
def new_index(request, extra_context=None):
    return _old_index(request, _add_to_context(request, extra_context))
def new_app_index(request, app_label, extra_context=None):
    return _old_app_index(request, app_label, _add_to_context(request, extra_context))


#Inject! because Python is cool
ModelAdmin.render_change_form = new_render_change_form
ModelAdmin.changelist_view = new_changelist_view
site.index = new_index
site.app_index = new_app_index

 