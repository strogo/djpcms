from django.db.models import Q
from django import http
from django.core.exceptions import ImproperlyConfigured

from django.contrib.admin import site, autodiscover, widgets
from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.contrib.admin import ModelAdmin, HORIZONTAL, VERTICAL
from django.contrib.admin import StackedInline, TabularInline
from django.contrib.admin import AdminSite, site, import_module

from djpcms.contrib.admin import actions
from djpcms.contrib.admin.forms import AutocompleteForeignKeyInput
from djpcms.contrib.admin.options import _add_to_context, construct_search


class Autocomplete(object):
    '''
    Register a model for autocomplete widget
    Usage, somewhere like urls:
    
    from djpcms.contrib.djpadmin import autocomplete
    
    autocomplete.register(MyModel,['field1,',field2',...])
    '''
    def __init__(self):
        self._register = {}
    
    def register(self, model, search_list):
        if model not in self._register:
            self._register[model] = search_list
    
    def get(self, model):
        return self._register.get(model,None)

autocomplete = Autocomplete()


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
                data = ''.join([u'%s|%s\n' % (getattr(f,rel_name),f.pk) for f in qs])
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

def log_addition(self, request, object):
    """
    Log that an object has been successfully added.

    The default implementation creates an admin LogEntry object.
    """
    from djpcms.contrib.admin.models import LogEntry, ADDITION
    LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(object).pk,
            object_id       = object.pk,
            object_repr     = force_unicode(object),
            action_flag     = ADDITION
        )

def log_change(self, request, object, message):
    """
    Log that an object has been successfully changed.

    The default implementation creates an admin LogEntry object.
    """
    from djpcms.contrib.admin.models import LogEntry, CHANGE
    LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(object).pk,
            object_id       = object.pk,
            object_repr     = force_unicode(object),
            action_flag     = CHANGE,
            change_message  = message
        )

def log_deletion(self, request, object, object_repr):
    """
    Log that an object has been successfully deleted. Note that since the
    object is deleted, it might no longer be safe to call *any* methods
    on the object, hence this method getting object_repr.

    The default implementation creates an admin LogEntry object.
    """
    from djpcms.contrib.admin.models import LogEntry, DELETION
    LogEntry.objects.log_action(
            user_id         = request.user.id,
            content_type_id = ContentType.objects.get_for_model(self.model).pk,
            object_id       = object.pk,
            object_repr     = object_repr,
            action_flag     = DELETION
        )

def history_view(self, request, object_id, extra_context=None):
    "The 'history' admin view for this model."
    from djpcms.contrib.admin.models import LogEntry
    model = self.model
    opts = model._meta
    app_label = opts.app_label
    action_list = LogEntry.objects.filter(
            object_id = object_id,
            content_type__id__exact = ContentType.objects.get_for_model(model).id
        ).select_related().order_by('action_time')
    # If no history was found, see whether this object even exists.
    obj = get_object_or_404(model, pk=unquote(object_id))
    context = {
            'title': _('Change history: %s') % force_unicode(obj),
            'action_list': action_list,
            'module_name': capfirst(force_unicode(opts.verbose_name_plural)),
            'object': obj,
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
    }
    context.update(extra_context or {})
    _add_to_context(request, context)
    context_instance = template.RequestContext(request, current_app=self.admin_site.name)
    return render_to_response(self.object_history_template or [
            "admin/%s/%s/object_history.html" % (app_label, opts.object_name.lower()),
            "admin/%s/object_history.html" % app_label,
            "admin/object_history.html"
        ], context, context_instance=context_instance)
            


ModelAdmin.render_change_form       = new_render_change_form
ModelAdmin.changelist_view          = new_changelist_view
ModelAdmin.delete_view              = new_delete_view
ModelAdmin.formfield_for_foreignkey = new_formfield_for_foreignkey
ModelAdmin.history_view             = history_view
ModelAdmin.log_addition             = log_addition
ModelAdmin.log_change               = log_change
ModelAdmin.log_deletion             = log_deletion
TabularInline.formfield_for_foreignkey = new_formfield_for_foreignkey
StackedInline.formfield_for_foreignkey = new_formfield_for_foreignkey







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


 