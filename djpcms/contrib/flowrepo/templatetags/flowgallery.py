from django.template import Library

from djpcms.contrib.flowrepo.models import Gallery

register = Library()

@register.inclusion_tag('flowrepo/jquery-cycle.html', takes_context=True)
def jquery_cycle(context, slug, width = 300, height = 150, type = "fade", speed = 1000, timeout = 5000):
    try:
        gallery = Gallery.objects.get(slug = slug)
        images  = gallery.images.all()
    except:
        gallery = None
        images = None
    return {
            'fade': 300,
            'gallery': gallery,
            'images': images,
            'width': width,
            'height': height,
            'type': type,
            'speed': speed,
            'timeout':timeout,
            }