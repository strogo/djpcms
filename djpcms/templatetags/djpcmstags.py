from djpcms import sites
from django import template

from djpcms.template import mark_safe
from djpcms.plugins import get_plugin


register = template.Library()


class DummyCompressorNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return self.nodelist.render(context)

@register.tag
def compress_if_you_can(parser, token):
    '''
    Compress media if django_compressor is available
    '''
    nodelist = parser.parse(('endcompress',))
    parser.delete_first_token()
    if 'djpcms.contrib.compressor' in sites.settings.INSTALLED_APPS:
        from djpcms.contrib.compressor.templatetags.compress import CompressorNode

        args = token.split_contents()

        if not len(args) == 2:
            raise template.TemplateSyntaxError("%r tag requires either 1, 3 or 5 arguments." % args[0])

        kind = args[1]
        if not kind in ['css', 'js']:
            raise template.TemplateSyntaxError("%r's argument must be 'js' or 'css'." % args[0])

        return CompressorNode(nodelist, kind)
    else:
        return DummyCompressorNode(nodelist)
    
@register.filter
def cleanjs(media):
    try:
        media._js.remove('%sjs/jquery.min.js' % sites.settings.ADMIN_MEDIA_PREFIX)
    except Exception, e:
        pass
    jss = media.render_js()
    return mark_safe(u'\n'.join(jss))

#@register.filter
#def djplugin(name,args = None):
#    '''
#    display a plugin
#    '''
#    plugin = get_plugin(name)
#    if plugin:
#        return plugin.render()
#    else:
#        return ''


def google_analytics():
    if sites.settings.GOOGLE_ANALYTICS_ID:
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
        """ % sites.settings.GOOGLE_ANALYTICS_ID
        return mark_safe(an)
    else:
        return u''
register.simple_tag(google_analytics)

def lloogg_analytics():
    if sites.settings.LLOOGG_ANALYTICS_ID:
        an = """
    <script type="text/javascript">
        lloogg_clientid = "%s";
    </script>
    <script type="text/javascript" src="http://lloogg.com/l.js?c=%s">
    </script>
        """ % (sites.settings.LLOOGG_ANALYTICS_ID,sites.settings.LLOOGG_ANALYTICS_ID)
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
    murl = sites.settings.MEDIA_URL
    css = ['<link rel="stylesheet" type="text/css" href="%sdjpcms/jquery-ui-css/%s.css"/>' % (murl,DJPCMS_SITE_STYLE),
           '<link rel="stylesheet" type="text/css" href="%sdjpcms/djpcms.css"/>' % murl,
           '<link rel="stylesheet" type="text/css" href="%sdjpcms/jquery-ui-css/%s/jquery-ui-1.7.2.custom.css"/>' % (murl,DJPCMS_SITE_STYLE),
           '<link rel="stylesheet" type="text/css" href="%sdjpcms/jquery-ui-css/%s.css"/>' % (murl,DJPCMS_SITE_STYLE),
           '<link rel="stylesheet" type="text/css" href="%ssite/layout.css"/>' % murl]
    return mark_safe(u'\n'.join(css))
styling = register.simple_tag(styling)