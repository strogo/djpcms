from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.template import loader
   
class jsonbase(object):

    def dict(self):
        '''
        This is the only functions that needs to be implemented by derived
        classes
        '''
        pass

    def _dump(self,elem):
        '''
        Use JSON to serialize elem
        '''
        return simplejson.dumps(elem)
    
    def dumps(self):
        return self._dump(self.dict())
    
    def tojson(self):
        try:
            return mark_safe(force_unicode('%s' % self.dumps()))
        except Exception, e:
            return self.handleError(e)
    
    def handleError(self, e):
        return mark_safe(force_unicode(e))
    
    def error(self):
        return False
    
    
    
class simplelem(jsonbase):
    
    def __init__(self, elem):
        self.elem = elem
    
    def dict(self):
        return self.elem

class simpledump(object):
    
    def __init__(self, str):
        self.data = str
        
    def dumps(self):
        return self.data



class HeaderBody(jsonbase):
    '''
    Base class for 
    '''
    def dict(self):
        return self._dict(self.header(), self.body())
    
    def header(self):
        return ''
    
    def body(self):
        return ''
    
    def _dict(self,hd,bd):
        return {'header': hd,
                'body':   bd,
                'error':  self.error()}
        
    def handleError(self, e):
        js = self._dump(self._dict('server-error', e))
        return mark_safe(force_unicode(js))


class jempty(HeaderBody):
    
    def header(self):
        return 'empty'



class jservererror(HeaderBody):
    
    def __init__(self, err, url = None):
        self.html = loader.render_to_string(['bits/post-error.html',
                                             'djpcms/bits/post-error.html'],
                                            {'error':mark_safe(err),
                                             'url': url})
    
    def header(self):
        return 'servererror'
    
    def body(self):
        return self.html
    

class jhtmls(HeaderBody):
    '''
    Contains a list of objects
        {identifier, html and type}
    '''
    def __init__(self, html = None, identifier = None, alldocument = True, type = 'replace'):
        self.html = {}
        if html != None:
            self.add(identifier, html, type, alldocument)
    
    def header(self):
        return 'htmls'
    
    def __update(self, obj):
        html = self.html
        key  = obj.get('identifier')
        objr = html.get(key,None)
        if objr == None:
            html[key] = obj
        else:
            objr['html'] += obj['html']
        
    def add(self, identifier, html, type = 'replace', alldocument = False):
        obj = {'identifier':    identifier,
               'html':          html,
               'type':          type,
               'alldocument':   alldocument}
        self.__update(obj)
        
    def update(self, html):
        if isinstance(html,jhtmls):
            html = html.html
        for v in html.values():
            self.__update(v)
        
    def body(self):
        return list(self.html.values())


class jerrors(jhtmls):
    
    def __init__(self, **kwargs):
        super(jerrors,self).__init__(**kwargs)
        
    def error(self):
        return True


class jremove(HeaderBody):
    
    def __init__(self, identifier, alldocument = True):
        self.identifiers = []
        self.add(identifier, alldocument)
        
    def add(self, identifier, alldocument = True):
        self.identifiers.append({'identifier': identifier,
                                 'alldocument': alldocument})
    
    def header(self):
        return 'remove'
    
    def body(self):
        return self.identifiers
        

class jredirect(HeaderBody):
    '''
    Redirect to new url
    '''
    def __init__(self, url):
        self.url = url
        
    def header(self):
        return 'redirect'
        
    def body(self):
        return self.url
    