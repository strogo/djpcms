from django.utils.encoding import smart_str, force_unicode, smart_unicode


def todict(q):
    d = {}
    for k,v in q.items():
        d[k] = v
    return d

def form_kwargs(request, instance = None, withrequest = False, **kwargs):
    '''
    Quick form arguments aggregator
    
    Usage:
      def someview(request):
          form = MyForm(**form_kwargs(request))
    '''
    if request and request.method == 'POST':
        kwargs['data'] = request.POST
        kwargs['files'] = request.FILES
    if withrequest:
        kwargs['request'] = request
    if instance:
        kwargs['instance'] = instance
    return kwargs


def data2url(url,data):
    ps = []
    for k,v in data.items():
        v = v or ''
        ps.append('%s=%s' % (k,v))
    p = '&'.join(ps)
    return u'%s?%s' % (url,p)


class UnicodeObject(object):
    
    def __repr__(self):
        try:
            u = unicode(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
            u = '[Bad Unicode data]'
        return smart_str(u'<%s: %s>' % (self.__class__.__name__, u))

    def __str__(self):
        if hasattr(self, '__unicode__'):
            return force_unicode(self).encode('utf-8')
        return '%s object' % self.__class__.__name__


class requestwrap(UnicodeObject):
    
    def __init__(self, obj, request):
        self.request = request
        self.obj = obj
        
    def __unicode__(self):
        return unicode(self.obj)
        
    def __getattr__(self, name):
        attr = getattr(self.obj,name,None)
        if attr and callable(attr):
            # First we try using request as argument
            try:
                return attr(self.request)
            except:
                return attr()
        else:
            return attr