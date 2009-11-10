from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.http import require_POST
from django.contrib import comments
from django.contrib.comments import signals
from utils import next_redirect, confirmation_view

from djpcms.html import quickform, formlet
from djpcms.settings import HTML_CLASSES


class CommentPostBadRequest(http.HttpResponseBadRequest):
    """
    Response returned when a comment post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(CommentPostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("comments/400-debug.html", {"why": why})
            


def commentform(request, object, data = None, template = 'djpcms/comments/commentform.html'):
    cf = comments.get_form()(object, data = data)
    return quickform(form = cf,
                     cn = HTML_CLASSES.ajax_form,
                     template = template,
                     submitname = 'publish_comment',
                     submitvalue = 'Publish',
                     request = request,
                     url = '/comments/post/')            
            

def returnjs(data):
    return http.HttpResponse(data.dumps(), mimetype='application/javascript')

def post_comment(request, next=None):
    """
    Post a comment.

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``comments/preview.html``, will be rendered.
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    user = request.user
    if user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = user.get_full_name() or user.username
        if not data.get('email', ''):
            data["email"] = user.email

    # Check to see if the POST data overrides the view's next argument.
    next = data.get("next", next)
    
    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    
    df = quickform()
    if ctype is None or object_pk is None:
        return returnjs(df.errorpost("Missing content_type or object_pk field."))
    try:
        model  = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except TypeError:
        return returnjs(df.errorpost("Invalid content_type value: %r" % escape(ctype)))
    except AttributeError:
        return returnjs(df.errorpost("The given content-type %r does not resolve to a valid model." % escape(ctype)))
    except ObjectDoesNotExist:
        return returnjs(df.errorpost("No object matching content-type %r and object PK %r exists." % (escape(ctype), escape(object_pk))))

    # Do we want to preview the comment?
    preview = "preview" in data
    
    # Construct the comment form
    form = comments.get_form()(target, data=data)
    flet = formlet(form = form)

    # Check security information
    if form.security_errors():
        errs = escape(str(form.security_errors()))
        return returnjs(df.errorpost("The comment form failed security verification: %s" % errs))

    # If there are errors or if we requested a preview show the comment
    if not flet.is_valid():
        return returnjs(flet.jerrors)
        
    if preview:
        template_list = [
            "comments/%s_%s_preview.html" % tuple(str(model._meta).split(".")),
            "comments/%s_preview.html" % model._meta.app_label,
            "comments/preview.html",
            ]
        return render_to_response(
            template_list, {
                "comment" : form.data.get("comment", ""),
                "form" : form,
                "next": next,
                },
                RequestContext(request, {})
            )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response == False:
            returnjs(df.errorpost("comment_will_be_posted receiver %r killed the comment" % receiver.__name__))

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    return returnjs(df.messagepost("Comment submitted succesfully"))

post_comment = require_POST(post_comment)

comment_done = confirmation_view(
    template = "comments/posted.html",
    doc = """Display a "comment was posted" success page."""
)
