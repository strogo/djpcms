from django import template
from django.utils.safestring import mark_safe

from djpcms.settings import GOOGLE_ANALYTICS_ID, DJPCMS_SITE_STYLE
from django.conf import settings

register = template.Library()

ganalytics = u'''<script type="text/javascript"> 
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script> 
<script type="text/javascript"> 
var pageTracker = _gat._getTracker("%s");
pageTracker._initData();
pageTracker._trackPageview();
</script>'''


def google_analytics():
    if not GOOGLE_ANALYTICS_ID:
        return u''
    return mark_safe(ganalytics % GOOGLE_ANALYTICS_ID)
google_analytics = register.simple_tag(google_analytics)

def styling():
    murl = settings.MEDIA_URL
    css = ['<link rel="stylesheet" type="text/css" href="%sdjpcms/jquery-ui-css/%s.css"/>' % (murl,DJPCMS_SITE_STYLE),
           '<link rel="stylesheet" type="text/css" href="%sdjpcms/djpcms.css"/>' % murl,
           '<link rel="stylesheet" type="text/css" href="%slayout.css"/>' % murl,
           '<link rel="stylesheet" type="text/css" href="%s%s.css"/>' % (murl,DJPCMS_SITE_STYLE)]
    return mark_safe(u'\n'.join(css))
styling = register.simple_tag(styling)