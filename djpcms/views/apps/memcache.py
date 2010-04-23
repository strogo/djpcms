import math

from django.core.cache import cache
from django.conf.urls.defaults import url
from django.template import loader

from djpcms.utils.ajax import jhtmls
from djpcms.views.appsite import ApplicationBase
from djpcms.views.appview import AppViewBase
from djpcms.plugins import register_application

def round(v, p = 2):
    m = math.pow(10,p)
    return int(m*v)/m

def nstr(v,name):
    if v == 1:
        return '1 %s' % name
    elif v > 1:
        return '%s %ss' % (v,name)
    else:
        return ''
    
def nicetime(s):
    m = s/60
    if m:
        h = m/60
        if h:
            d = h/24
            if d:
                h -= 24*d
                return '%s %s' % (nstr(d,'day'),nstr(h,'hour'))
            else:
                return nstr(h,'hour')
        else:
            return nstr(m,'minute')
    else:
        return nstr(s,'second')

def get_stats():
    stats = cache._cache.get_stats()
    servers = []
    for s in stats:
        st = s[1]
        servers.append({'name':s[0],
                        'stats':st})
        uptime = st.get('uptime',0)
        bytes  = st.get('bytes',0)
        st['uptime'] = nicetime(int(uptime))
        mbytes = int(bytes)/1024.0
        if mbytes > 1:
            mbytes = round(mbytes,1)
        else:
            mbytes = round(mbytes,3)
        st['megabytes'] = mbytes
    return servers


class Index(AppViewBase):
    
    def __init__(self, app, parent = None):
        AppViewBase.__init__(self, parent = parent)
        self.appmodel = app
        
    def render(self, djp, **kwargs):
        try:
            servers  = get_stats()
            if servers:
                flashurl = '%sflush/' % self.appmodel.baseurl
                return loader.render_to_string('djpcms/bits/memcached.html',
                                               {'servers':servers,
                                                'url': flashurl})
            else:
                return u''
        except:
            return 'Memcached not installed'
    
class Flush(AppViewBase):
    _methods      = ('post',)
    
    def __init__(self, app, parent = None):
        AppViewBase.__init__(self, parent = parent)
        self.appmodel = app
        
    def default_post(self, djp):
        try:
            cache._cache.flush_all()
            servers  = get_stats()
            html = loader.render_to_string('djpcms/bits/memcached.html',
                                           {'servers':servers})
            return jhtmls(html, '#memcached-panel')
        except:
            pass


class MemcacheApplication(ApplicationBase):
    name = 'memcache-monitor'
    
    def __init__(self, baseurl, application_site, editavailable):
        super(MemcacheApplication,self).__init__(baseurl, application_site, editavailable)       
        self.root_application   = Index(self)
        self.flush              = Flush(self,self.root_application)
        register_application(self.root_application,'memcache-monitor','Memcached Monitor')
        self.urls = (url(r'^$', self.root_application),
                     url(r'^flush/$', self.flush),
                    )
