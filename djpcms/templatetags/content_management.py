from django import template
from django.utils.safestring import mark_safe

from djpcms.settings import HTML_CLASSES
from djpcms.models import SiteContent
from djpcms.html import htmlPlugin, div, box, ajaxeditlink, ajaxdeletelink

from djpcms.views.content.editcontent import contentselectform, contenteditview, contentdeleteview, contentid

register = template.Library()


content_box_types = ((0,'simple'),
                     (1,'simple box'))


def content_box(vr, pos, ctype = 0, cn = None):
    try:
        view     = vr.view
        contents = view.page.description.split(' ')
        hd       = None
        bd       = u''
        content  = None
        
        if len(contents) > pos:
            try:
                code    = contents[pos]
                content = SiteContent.objects.get_from_code(code)
            except Exception, e:
                bd = u'%s' % e

            if content:
                try:
                    bd      = content.htmlbody()
                except Exception, e:
                    bd = u'%s' % e

        # we are in editing mode
        if view.editurl:
            request = vr.request
            editview = contenteditview(request, pos, view.page)
            delview  = contentdeleteview(request, pos, view.page)
            cselect  = editview.get_selectform(request)
            hd       = htmlPlugin()
            hd.append(cselect)
            hd.append(ajaxeditlink(url = editview.url))
            hd.append(ajaxdeletelink(url = delview.url))
            # wrap the body with the editing div
            bd = div(id = contentid(pos), inner = bd)
            return box(hd = hd, bd = bd)
        
        if ctype == 1:
            return box(hd = hd, bd = bd, cn = cn)
        elif ctype == 0:
            return div(inner = bd, cn = cn)
    except Exception, e:
        return box(hd = 'Error', bd = str(e))


def content_simple_box(vr, pos):
    return content_box(vr, pos, 1)
content_simple_box = register.filter(content_simple_box)

@register.filter
def content_intro_div(vr, pos):
    return content_box(vr, pos, 0, cn = 'intro')

def content_simple(view, pos):
    return content_box(view, pos, 0, cn = HTML_CLASSES.content_simple)
content_simple = register.filter(content_simple)


def grid_orizontal_separator(view, height):
    return mark_safe(u'<div style="width:%s; height:%spx"></div>' % ('100%',height)) 
grid_orizontal_separator = register.filter(grid_orizontal_separator)

