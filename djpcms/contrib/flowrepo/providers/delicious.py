import time
import dateutil.parser
import dateutil.tz
import logging
import urllib

from django.conf import settings
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.utils.dateformat import format
from django.contrib.auth.models import User

from flowrepo import settings as flowsettings
from flowrepo.providers import utils
from flowrepo.models import FlowItem, Bookmark

#
# Super-mini Delicious API
#
class DeliciousClient(object):
    """
    A super-minimal delicious client :)
    """
    _deliciousApiHost = 'https://api.del.icio.us/'
    lastcall = 0

    def __init__(self, username, password, method='v1'):
        self.username, self.password = username, password
        self.method = method

    def __getattr__(self, method):
        return DeliciousClient(self.username, self.password, '%s/%s' % (self.method, method))

    def __repr__(self):
        return "<DeliciousClient: %s>" % self.method

    def __call__(self, **params):
        # Enforce Yahoo's "no calls quicker than every 1 second" rule
        delta = time.time() - DeliciousClient.lastcall
        if delta < 2:
            time.sleep(2 - delta)
        DeliciousClient.lastcall = time.time()
        url = ('%s%s?' % (self._deliciousApiHost,self.method)) + urllib.urlencode(params)     
        return utils.getxml(url, username=self.username, password=self.password)

#
# Public API
#

log = logging.getLogger("flowrepo.providers.delicious")

def enabled():
    return flowsettings.DELICIOUS_USERNAME and flowsettings.DELICIOUS_PASSWORD
        

def update(c = 0):
    user = User.objects.get(id = flowsettings.FOR_USER_ID)
    if c:
        items = FlowItem.objects.get_for_user(user,Bookmark)
        for item in items:
            if item.object:
                item.object.delete()
            item.delete()
    delicious = DeliciousClient(flowsettings.DELICIOUS_USERNAME, flowsettings.DELICIOUS_PASSWORD)

    # Check to see if we need an update
    last_update_date = FlowItem.objects.get_last_update_of_model(Bookmark, interactive = False)
    last_post_date   = utils.parsedate(delicious.posts.update().get("time"))

    # First we sync bookmarks which have been added or edited on the site
    books = FlowItem.objects.get_interactive_for_model(Bookmark)
    if books:
        log.info("Found %s bookmarks changed or added on the site: sync with delicious", books.count())
        for b in books:
            if not addnew(delicious, b):
                log.warn('Problem while syncronising bookmark %s with delicious' % b.url)
    
    if last_post_date <= last_update_date:
        log.info("Skipping update: last update date: %s; last post date: %s", last_update_date, last_post_date)
        return

    for datenode in reversed(list(delicious.posts.dates().getiterator('date'))):
        dt = utils.parsedate(datenode.get("date")).date()
        ld = last_update_date.date()
        if dt >= ld:
            log.debug("Checking delicious bookmarks for date %s" % format(dt,settings.DATE_FORMAT))
            _update_bookmarks_from_date(delicious, dt, user)

#
# Private API
#

ISO_8601_DATETIME = '%Y-%m-%dT%H:%M:%SZ'

def delicious_datetime(str):
    """
    Parse a ISO 8601 formatted string to a Python datetime
    """
    return datetime.datetime(*time.strptime(str, ISO_8601_DATETIME)[0:6])

def date2delicious(dt):
    '''
    Convert a Python datetime object into a delicious string
    '''
    v = dt.strftime(ISO_8601_DATETIME)
    return v


def postinfo(xml):
    return dict((k, smart_unicode(xml.get(k))) for k in xml.keys())


def _update_bookmarks_from_date(delicious, dt, user):
    log.debug("Reading bookmarks from %s", dt)
    xml = delicious.posts.get(dt=dt.strftime("%Y-%m-%d"))
    for post in xml.getiterator('post'):
        info = postinfo(post)
        url  = info['href']
        if (info.has_key("shared") and flowsettings.DELICIOUS_GETDNS) or (not info.has_key("shared")):
            log.debug("Handling bookmark for %r", url)
            _handle_bookmark(info, user)
        else:
            log.debug("Skipping bookmark for %r, app settings indicate to ignore bookmarks marked \"Do Not Share\"", info["href"])
_update_bookmarks_from_date = transaction.commit_on_success(_update_bookmarks_from_date)


def addnew(delicious, item):
    '''
    Add a new bookmark to delicious
    '''
    instance = item.object
    if item.visibility == 3:
        shared = 'yes'
    else:
        shared = 'no'
    xml  = delicious.posts.add(url = item.url,
                               description = instance.name,
                               extended = instance.description,
                               dt       = date2delicious(item.timestamp),
                               tags     = item.tags,
                               replace  = 'yes',
                               shared   = shared)
    info = postinfo(xml)
    if info.get('code','failed') == 'done':
        xml  = delicious.posts.get(url = item.url, meta = 'yes')
        for post in xml.getiterator('post'):
            info = postinfo(post)
            item.source_id = info['hash']
            item.save(source = __name__)
            log.debug('Updated %s' % item.url)
            return True
    else:
        return False
    
def syncmod(delicious, items):
    hashes = [item.source_id for item in items]
    xml    = delicious.posts.get(hashes = u'+'.join(hashes), meta = 'yes')
    for post in xml.getiterator('post'):
        info = postinfo(post)
        hash = info['hash']
        item = items.get(source_id = hash)
        url  = info['href']
        if item.url != url:
            delicious.posts.delete(url)
        addnew(delicious, item)


def _handle_bookmark(info, user):
    b, created = Bookmark.objects.get_or_create(
            url = info['href'],
            defaults = dict(
                            name = info['description'],
                            extended = info.get('extended', ''),
                            )
            )
    if not created:
        b.name = info['description']
        b.extended = info.get('extended', '')
        b.save()
    
    visibility = 3
    if info.get('shared','yes') == 'no':
        visibility = 1
    return FlowItem.objects.create_or_update(
        b,
        user = user, 
        timestamp = utils.parsedate(info['time']), 
        tags = info.get('tag', ''),
        source = __name__,
        source_id = info['hash'],
        visibility = visibility
    )
