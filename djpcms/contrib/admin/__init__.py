from django.contrib.admin import autodiscover, widgets
from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.contrib.admin import ModelAdmin, HORIZONTAL, VERTICAL
from django.contrib.admin import StackedInline, TabularInline
from django.contrib.admin import AdminSite, site
from django.utils.importlib import import_module

from djpcms.contrib.admin import actions
from djpcms.contrib.admin.options import _add_to_context, construct_search
from djpcms.contrib.admin.options import log_addition, log_change, log_deletion, history_view
from djpcms.utils.html import autocomplete, AutocompleteForeignKeyInput

from django.db.models import Q
from django import http, forms
from django.core.exceptions import ImproperlyConfigured


import temp
#Inject to ModelAdmin class. Nice. Because Python is cool!!!!!!!!!!!!!

_old_render_change_form         = ModelAdmin.render_change_form
_old_changelist_view            = ModelAdmin.changelist_view
_old_delete_view                = ModelAdmin.delete_view

def new_render_change_form(self, request, context, **kwargs):
    return _old_render_change_form(self, request, _add_to_context(request, context), **kwargs)
def new_delete_view(self, request, object_id, extra_context=None):
    return _old_delete_view(self, request, object_id, _add_to_context(request, extra_context))

def new_changelist_view(self, request, extra_context=None):
    if request.is_ajax():
        # we are searching
        if request.method == "GET":
            params = dict(request.GET.items())
            query = request.GET.get('q', None)
            search_fields = autocomplete.get(self.model)
            if query and search_fields:
                q = None
                for field_name in search_fields:
                    name = construct_search(field_name)
                    if q:
                        q = q | Q( **{str(name):query} )
                    else:
                        rel_name = name.split('__')[0]
                        q = Q( **{str(name):query} )
                qs = self.model.objects.filter(q)                    
                data = ''.join([u'%s|%s|%s\n' % (getattr(f,rel_name),f,f.pk) for f in qs])
                return http.HttpResponse(data)
            return http.HttpResponseNotFound()
        else:
            return http.HttpResponseNotFound()
    else:
        return _old_changelist_view(self, request, _add_to_context(request, extra_context))


def new_formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    """
    Get a form Field for a ForeignKey.
    """
    db = kwargs.get('using')
    search_fields = autocomplete.get(db_field.rel.to)
    if search_fields:
        kwargs['widget'] = AutocompleteForeignKeyInput(db_field.rel,search_fields)
    elif db_field.name in self.raw_id_fields:
        kwargs['widget'] = widgets.ForeignKeyRawIdWidget(db_field.rel, using=db)
    elif db_field.name in self.radio_fields:
        kwargs['widget'] = widgets.AdminRadioSelect(attrs={
            'class': get_ul_class(self.radio_fields[db_field.name]),
        })
        kwargs['empty_label'] = db_field.blank and _('None') or None
        
    return db_field.formfield(**kwargs)

def new_formfield_for_manytomany(self, db_field, request=None, **kwargs):
    """
    Get a form Field for a ManyToManyField.
    """
    # If it uses an intermediary model that isn't auto created, don't show
    # a field in admin.
    if not db_field.rel.through._meta.auto_created:
        return None
    db = kwargs.get('using')

    if db_field.name in self.raw_id_fields:
        kwargs['widget'] = widgets.ManyToManyRawIdWidget(db_field.rel, using=db)
        kwargs['help_text'] = ''
    elif db_field.name in (list(self.filter_vertical) + list(self.filter_horizontal)):
        kwargs['widget'] = widgets.FilteredSelectMultiple(db_field.verbose_name, (db_field.name in self.filter_vertical))


# Injecting!!! 
#
ModelAdmin.render_change_form       = new_render_change_form
ModelAdmin.changelist_view          = new_changelist_view
ModelAdmin.delete_view              = new_delete_view
ModelAdmin.history_view             = history_view
ModelAdmin.log_addition             = log_addition
ModelAdmin.log_change               = log_change
ModelAdmin.log_deletion             = log_deletion

ModelAdmin.formfield_for_foreignkey    = new_formfield_for_foreignkey
TabularInline.formfield_for_foreignkey = new_formfield_for_foreignkey
StackedInline.formfield_for_foreignkey = new_formfield_for_foreignkey

ModelAdmin.formfield_for_manytomany    = new_formfield_for_manytomany
TabularInline.formfield_for_manytomany = new_formfield_for_manytomany
StackedInline.formfield_for_manytomany = new_formfield_for_manytomany



#Inject to site object. Nice. Because Python is sooooooooo cool!!!!!!!!!!!!!

_old_index              = site.index
_old_app_index          = site.app_index

def new_index(request, extra_context=None):
    return _old_index(request, _add_to_context(request, extra_context))
def new_app_index(request, app_label, extra_context=None):
    return _old_app_index(request, app_label, _add_to_context(request, extra_context))
def new_check_dependencies():
    from djpcms.contrib.admin.models import LogEntry
    from django.contrib.contenttypes.models import ContentType

    if not LogEntry._meta.installed:
        raise ImproperlyConfigured("Put 'djpcms.contrib.admin' in your "
            "INSTALLED_APPS setting in order to use the admin application.")
        if not ContentType._meta.installed:
            raise ImproperlyConfigured("Put 'django.contrib.contenttypes' in "
                "your INSTALLED_APPS setting in order to use the admin application.")
        if not ('django.contrib.auth.context_processors.auth' in settings.TEMPLATE_CONTEXT_PROCESSORS or
            'django.core.context_processors.auth' in settings.TEMPLATE_CONTEXT_PROCESSORS):
            raise ImproperlyConfigured("Put 'django.contrib.auth.context_processors.auth' "
                "in your TEMPLATE_CONTEXT_PROCESSORS setting in order to use the admin application.")

site.index = new_index
site.app_index = new_app_index
site.check_dependencies = new_check_dependencies



