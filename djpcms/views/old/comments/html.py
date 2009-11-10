
from django.contrib.comments.models import Comment

from djpcms.html import div, htmlPlugin, box, TemplatePlugin


def comment_html(c):
    p = TemplatePlugin(template='djpcms/comments/comment.html')
    p.comment = c
    return p

def get_comments(request, object, name = 'post'):
    cs = Comment.objects.for_model(object).filter(is_public = True)
    if cs:
        if cs.count() == 1:
            hd = 'There is one comment for this %s' % name
        else:
            hd = 'There are %s comments for this %s' % (cs.count(),name)
        bd = htmlPlugin()
        for c in cs:
            bd.append(comment_html(c))
        return box(hd = hd, bd = bd, cn = 'djpcms-comment', rounded = False)