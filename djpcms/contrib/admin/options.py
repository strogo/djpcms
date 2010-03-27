from django.utils.encoding import force_unicode
from django.contrib.contenttypes.models import ContentType

from djpcms.utils.navigation import Navigator
from djpcms.utils.html import grid960


# Aijack admin site to inject some specific djpcms stuff

def _add_to_context(request, context):
    from djpcms.conf import settings
    from djpcms.views.cache import pagecache
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


def construct_search(field_name):
    # use different lookup methods depending on the notation
    if field_name.startswith('^'):
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]
    else:
        return "%s__icontains" % field_name



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
            

