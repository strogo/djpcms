from django.contrib.admin import site, autodiscover
from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.contrib.admin import ModelAdmin, HORIZONTAL, VERTICAL
from django.contrib.admin import StackedInline, TabularInline
from django.contrib.admin import AdminSite, site, import_module

from djpcms.contrib.admin import actions
from djpcms.contrib.admin.options import _add_to_context

class Autocomplete(object):
    
    def __init__(self):
        self._register = {}
    
    def register(self, model):
        if model not in self._register:
            self._register.append(model)

autocomplete = Autocomplete()


#Inject to ModelAdmin class. Nice. Because Python is cool!!!!!!!!!!!!!

_old_render_change_form = ModelAdmin.render_change_form
_old_changelist_view    = ModelAdmin.changelist_view
_old_delete_view        = ModelAdmin.delete_view

def new_render_change_form(self, request, context, **kwargs):
    return _old_render_change_form(self, request, _add_to_context(request, context), **kwargs)
def new_changelist_view(self, request, extra_context=None):
    return _old_changelist_view(self, request, _add_to_context(request, extra_context))
def new_delete_view(self, request, object_id, extra_context=None):
    return _old_delete_view(self, request, object_id, _add_to_context(request, extra_context))

ModelAdmin.render_change_form   = new_render_change_form
ModelAdmin.changelist_view      = new_changelist_view
ModelAdmin.delete_view          = new_delete_view



#Inject to site object. Nice. Because Python is sooooooooo cool!!!!!!!!!!!!!

_old_index              = site.index
_old_app_index          = site.app_index

def new_index(request, extra_context=None):
    return _old_index(request, _add_to_context(request, extra_context))
def new_app_index(request, app_label, extra_context=None):
    return _old_app_index(request, app_label, _add_to_context(request, extra_context))

site.index = new_index
site.app_index = new_app_index



 