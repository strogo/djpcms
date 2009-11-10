from django import template
from django.conf import settings

from djpcms.settings import HTML_CLASSES
register = template.Library()

def _google_feeds(dynamic = True, stacked = False):
    """
    Returns the string contained in the setting MEDIA_URL
    """
    murl = settings.MEDIA_URL
    return template.loader.render_to_string('djpcms/bits/google-feed.html',
                                            {'media_url': murl,
                                             'api_key': settings.GOOGLE_AJAX_FEED_API_KEY,
                                             'feed_class': HTML_CLASSES.FEEDS_HTML_CLASS,
                                             'dynamic': dynamic})

def dynamic_feeds():
    return _google_feeds(True)
dynamic_feeds = register.simple_tag(dynamic_feeds)