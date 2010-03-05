from django import template

from djpcms.utils import mark_safe
from djpcms.conf import settings

register = template.Library()


def google_analytics():
    if settings.GOOGLE_ANALYTICS_ID:
        an = """
    <script type="text/javascript">
        var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
        document.write(unescape("%%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%%3E%%3C/script%%3E"));
    </script>
    <script type="text/javascript">
        var pageTracker = _gat._getTracker("%s");
        pageTracker._initData();
        pageTracker._trackPageview();
    </script>
        """ % settings.GOOGLE_ANALYTICS_ID
        return mark_safe(an)
    else:
        return u''
register.simple_tag(google_analytics)

def lloogg_analytics():
    if settings.LLOOGG_ANALYTICS_ID:
        an = """
    <script type="text/javascript">
        lloogg_clientid = "%s";
    </script>
    <script type="text/javascript" src="http://lloogg.com/l.js?c=%s">
    </script>
        """ % (settings.LLOOGG_ANALYTICS_ID,settings.LLOOGG_ANALYTICS_ID)
        return mark_safe(an)
    else:
        return ''
register.simple_tag(lloogg_analytics)

def _css_validator(version = 2, color = ''):
    if version == 1 or version == 2:
        src = "http://www.w3.org/Icons/valid-css%s%s.png" % (version,color)
    else:
        src = "#"
    va = """
    <a href="http://jigsaw.w3.org/css-validator/" title="Validate CSS code">
    <img src="%s" alt="W3C CSS %s"/></a>
    """ % (src,version)
    return mark_safe(va)

def css_validator(level = 2):
    return _css_validator(level)
register.simple_tag(css_validator)
def blue_css_validator(level = 2):
    return _css_validator(level,"-blue")
register.simple_tag(blue_css_validator)

def styling():
    murl = settings.MEDIA_URL
    css = ['<link rel="stylesheet" type="text/css" href="%sdjpcms/jquery-ui-css/%s.css"/>' % (murl,DJPCMS_SITE_STYLE),
           '<link rel="stylesheet" type="text/css" href="%sdjpcms/djpcms.css"/>' % murl,
           '<link rel="stylesheet" type="text/css" href="%sdjpcms/jquery-ui-css/%s/jquery-ui-1.7.2.custom.css"/>' % (murl,DJPCMS_SITE_STYLE),
           '<link rel="stylesheet" type="text/css" href="%sdjpcms/jquery-ui-css/%s.css"/>' % (murl,DJPCMS_SITE_STYLE),
           '<link rel="stylesheet" type="text/css" href="%ssite/layout.css"/>' % murl]
    return mark_safe(u'\n'.join(css))
styling = register.simple_tag(styling)