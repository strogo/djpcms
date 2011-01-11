'''Introduces several utility classes for handling JSON AJAX
interaction with ``djpcms.js``
'''
import json
from djpcms.template import handle
from djpcms.utils import force_str
from djpcms.utils.collections import OrderedDict

   
class jsonbase(object):
    '''Base class for JSON AJAX utilities'''
    
    def dict(self):
        '''This is the only functions that needs to be implemented by derived
classes. It converts ``self`` into a dictionary ready to be serialised
as JSON string.
        '''
        raise NotImplementedError

    def _dump(self, elem):
        # Internal function which uses json to serialise elem
        return json.dumps(elem)
    
    def dumps(self):
        '''Serialize ``self`` as a ``JSON`` string'''
        return self._dump(self.dict())
    
    def tojson(self, autoescape = True):
        t = handle()
        try:
            s = force_str(self.dumps())
            return s if not autoescape else t.mark_safe(s)
        except Exception as e:
            return self.handleError(e, autoescape)
    
    def handleError(self, e, autoescape = True):
        t = handle()
        s = force_str(e)
        return s if not autoescape else t.mark_safe(s)
    
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
    '''Base class for interacting with ``$.djpcms.jsonCallBack`` in
``djpcms.js``. 
    '''
    def dict(self):
        return self._dict(self.header(), self.body())
    
    def header(self):
        '''Type of element recognized by ``$.djpcms.jsonCallBack``'''
        return ''
    
    def body(self):
        return ''
    
    def _dict(self,hd,bd):
        return {'header': hd,
                'body':   bd,
                'error':  self.error()}
        
    def handleError(self, e):
        js = self._dump(self._dict('server-error', e))
        return mark_safe(force_str(js))


class jempty(HeaderBody):
    
    def header(self):
        return 'empty'


class jservererror(HeaderBody):
    
    def __init__(self, err, url = None):
        loader = handle()
        self.html = loader.render_to_string(['bits/post-error.html',
                                             'djpcms/bits/post-error.html'],
                                            {'error':loader.mark_safe(err),
                                             'url': url})
    
    def header(self):
        return 'servererror'
    
    def body(self):
        return self.html
    
    
class jerror(HeaderBody):
    
    def __init__(self, msg):
        self.html = msg
    
    def header(self):
        return 'error'
    
    def body(self):
        return self.html


class jcollection(HeaderBody):
    '''A collection of HeaderBody elements'''
    def __init__(self):
        self.data = []
        
    def header(self):
        return 'collection'
    
    def append(self, elem):
        if isinstance(elem,HeaderBody):
            self.data.append(elem)
            
    def body(self):
        return [d.dict() for d in self.data]
            
            
class jhtmls(HeaderBody):
    '''Contains a list of objects
        {identifier, html and type}
    '''
    def __init__(self, html = None, identifier = None, alldocument = True, type = 'replace'):
        self.html = OrderedDict()
        if html != None:
            self.add(identifier, html, type, alldocument)
    
    def header(self):
        return 'htmls'
    
    def __update(self, obj):
        html = self.html
        key  = obj.get('identifier')
        objr = html.get(key,None)
        if objr is None:
            html[key] = obj
        else:
            objr['html'] += obj['html']
        
    def add(self, identifier, html = '', type = 'replace', alldocument = True):
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


class jattribute(HeaderBody):
    '''Modify ``dom`` attributes'''
    def __init__(self):
        self.data = []
        
    def header(self):
        return 'attribute'
    
    def body(self):
        return self.data
    
    def add(self, selector, attribute, value, alldocument = True):
        '''Add a new attribute to modify:
        
        :parameter selector: jQuery selector for the element to modify.
        :parameter attribute: attribute name (``id``, ``name``, ``href``, ``action`` ex.).
        :parameter value: new value for attribute.
        :parameter selector: ``True`` if selector to be applied to al document.'''
        self.data.append({'selector':selector,
                          'attr':attribute,
                          'value':value,
                          'alldocument':alldocument})
        
        
class jclass(HeaderBody):
    '''Modify, delete or add a new class to a dom element.'''
    def __init__(self, selector, clsname, type = 'add'):
        self.selector = selector
        self.clsname = clsname
        self.type = type
        
    def header(self):
        return 'class'
    
    def body(self):
        return {'selector':self.selector,
                'clsname':self.clsname,
                'type':self.type}
    

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

    
class jpopup(jredirect):
    '''Contains a link to use for opening a popup windows'''
    
    def header(self):
        return 'popup'
    
    
class dialog(HeaderBody):
    '''
    jQuery UI dialog
    '''
    def __init__(self, hd = '', bd = None, **kwargs):
        self.bd         = bd
        self.options    = self.get_options(hd,**kwargs)
        self.buttons    = []
        
    def get_options(self, hd, **kwargs):
        return {'modal': kwargs.get('modal',False),
                'draggable': kwargs.get('draggable',True),
                'resizable': kwargs.get('resizable',True),
                'height':    kwargs.get('height','auto'),
                'width':     kwargs.get('width',300),
                'title':     hd,
                'dialogClass': kwargs.get('dialogClass','')}
        
    def header(self):
        return 'dialog'
    
    def body(self):
        return {'html':self.bd,
                'options':self.options,
                'buttons':self.buttons}
        
    def addbutton(self, name, url = None, func = None, close = True):
        self.buttons.append({'name':name,
                             'url':url,
                             'func':func,
                             'close':close})

