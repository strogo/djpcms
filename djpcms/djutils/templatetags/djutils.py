from django import template
from django.contrib.comments.templatetags.comments import CommentFormNode

register = template.Library()


def get_comment_form(parser, token):
    """
    Get a (new) form object to post a new comment.

    Syntax::

        {% get_comment_form for [object] as [varname] %}
        {% get_comment_form for [app].[model] [object_id] as [varname] %}
    """
    return CommentFormNode.handle_token(parser, token)


register.tag(render_comment_form)