import hashlib
import datetime
import logging
import dateutil
import re

from django.db import transaction
from django.template.defaultfilters import slugify
from django.utils.functional import memoize
from django.utils.http import urlquote
from django.utils.encoding import smart_str, smart_unicode
from django.contrib.auth.models import User

from httplib2 import HttpLib2Error

from flowrepo import settings
from flowrepo.providers import utils
from flowrepo.models import FlowItem, Message, ContentLink
from flowrepo.markups import get


#
# API URLs
#
RECENT_STATUSES_URL = "http://twitter.com/statuses/user_timeline/%s.rss?page=%s"
USER_URL = "http://twitter.com/%s"

#
# Public API
#

log = logging.getLogger("flowrepo.providers.twitter")

def enabled():
    if settings.TWITTER_USERNAME:
        return True
    else:
        log.warn('The Twitter provider is not available because the '
                 'TWITTER_USERNAME settings are undefined.')
        return False

def update(c = 0):
    user = User.objects.get(id = settings.FOR_USER_ID)
    if c:
        items = FlowItem.objects.get_for_user(user,Message)
        for item in items:
            if item.object:
                item.object.delete()
            item.delete()
    last_update_date = FlowItem.objects.get_last_update_of_model(Message,interactive = False)
    log.debug("Last update date: %s", last_update_date)
    
    page = 1
    go = True
    while go:
        go    = False
        xml   = utils.getxml(RECENT_STATUSES_URL % (settings.TWITTER_USERNAME,page))
        page += 1
        for status in xml.getiterator("item"):
            message      = status.find('title')
            message_text = smart_unicode(message.text)
            url          = smart_unicode(status.find('link').text)

            # pubDate delivered as UTC
            timestamp    = dateutil.parser.parse(status.find('pubDate').text)
            if settings.FLOWREPO_ADJUST_DATETIME:
                timestamp = utils.utc_to_local_datetime(timestamp)
            
            if Message.objects.filter(url = url):
                go = False
                break
                
            _handle_status(message_text, url, timestamp, user)
            go = True


if settings.TWITTER_TRANSFORM_MSG:
    USER_LINK_TPL = '[[%s|@%s]]'
    TAG_RE = re.compile(r'(?P<tag>\#\w+)')
    USER_RE     = re.compile(r'(?P<username>@\w+)')
    RT_RE       = re.compile(r'RT\s+(?P<username>@\w+)')
    USERNAME_RE = re.compile(r'^%s:'%settings.TWITTER_USERNAME)
    OH_RE       = re.compile(r'OH: "(?P<quote>[:,\s\.\w]+)"')

    # modified from django.forms.fields.url_re
    URL_RE = re.compile(
        r'https?://'
        r'(?:(?:[A-Z0-9-]+\.)+[A-Z]{2,6}|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/\S+|/?)', re.IGNORECASE)

    def _transform_retweet(matchobj):
        if '%s' in settings.TWITTER_RETWEET_TXT:
            return settings.TWITTER_RETWEET_TXT % matchobj.group('username')
        return settings.TWITTER_RETWEET_TXT

    def _transform_user_ref_to_link(matchobj):
        user = matchobj.group('username')[1:]
        link = USER_URL % user
        return USER_LINK_TPL % (link, user)

    def _parse_message(message_text):
        """
        Parse out some semantics for teh lulz.
        """
        links = list()
        tags = ""

        # remove newlines
        message_text = message_text.replace('\n','')
        # generate link list for ContentLink
        links = [ link for link in URL_RE.findall(message_text) ]
        link_ctr = 1
        link_dict = {}
        for link in URL_RE.finditer(message_text):
            link_dict[link.group(0)] = link_ctr
            link_ctr += 1
        generate_link_num = lambda obj: "[%d]"%link_dict[obj.group(0)]
        # remove URLs referenced in message content
        if settings.TWITTER_REMOVE_LINKS:
        	message_text = URL_RE.sub(generate_link_num,message_text)
        # remove leading username
        message_text = USERNAME_RE.sub('',message_text)
        # check for RT-type retweet syntax
        message_text = RT_RE.sub(_transform_retweet,message_text)
        # replace @user references with links to their timeline
        message_text = USER_RE.sub(_transform_user_ref_to_link,message_text)
        # generate tags list
        tags = ' '.join( [tag[1:] for tag in TAG_RE.findall(message_text)] )
        # extract defacto #tag style tweet tags
        if settings.TWITTER_REMOVE_TAGS:
            message_text = TAG_RE.sub('',message_text)
        return (message_text.strip(),links,tags)

    log.info("Enabling message transforms")
else:
    _parse_message = lambda msg: (msg,list(),"")
    log.info("Disabling message transforms")

#
# Private API
#

@transaction.commit_on_success
def _handle_status(message_text, url, timestamp, user):
    try:
        message_text, links, tags = _parse_message(message_text)
    except:
        log.error("Failed to parse message: %s" % message_text)
        return

    register = FlowItem.objects.unregisterModel(Message)
    t = Message(message = message_text,
                url = url)
    t.save()
    if register:
        FlowItem.objects.registerModel(Message)

    log.debug("Saving message: %r", message_text)
    try:
        item = FlowItem.objects.create_or_update(
                                                 t,
                                                 user = user,
                                                 timestamp = timestamp,
                                                 source = __name__,
                                                 source_id = '',
                                                 tags = tags,
                                                 )
    except:
        log.error("Failed to save message: %s" % message_text)
        t.delete()
        
        #for link in links:
        #    l = ContentLink(
        #        url = link,
        #        identifier = link,
        #        )
        #    l.save()
        #    t.links.add(l)


def _source_id(message_text, url, timestamp, user):
    return hashlib.md5(smart_str(message_text) + smart_str(url) + str(timestamp)).hexdigest()
    
def _status_exists(message_text, url, timestamp, user):
    id = _source_id(message_text, url, timestamp, user)
    try:
        FlowItem.objects.get(source=__name__, source_id=id)
    except FlowItem.DoesNotExist:
        return False
    else:
        return True
