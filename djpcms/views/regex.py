import copy

from django.utils.encoding import iri_to_uri

from djpcms.core.exceptions import ApplicationUrlException


class RegExUrl(object):
    '''Helper class for url regular expression manipulation
    
    .. attribute: url
    
        regular expression string
        
    .. attribute: split
        
        if True the url will be split using '/' as separator  
    '''
    def __init__(self, url = None, split = True, append_slash = True):
        self.url    = str(url or '')
        self.purl   = ''
        self.targs  = 0
        self.nargs  = 0
        self._split = split
        self.breadcrumbs = []
        self.names = []
        self.append_slash = append_slash
        if self.url:
            self.__process()
            if self.append_slash:
                self.url  = '%s/' % self.url
        
    def __len__(self):
        return len(self.url)
    
    def __eq__(self, other):
        if isinstance(other,self.__class__):
            return self.url == other.url
        else:
            return False
    
    def split(self):
        if self._split:
            return self.url.split('/')
        else:
            return ['%s' % self.url]
        
    def __str__(self):
        if self.append_slash:
            return '^%s$' % self.url
        else:
            return self.url

    def get_url(self, **kwargs):
        if kwargs:
            return iri_to_uri(self.purl % kwargs)
        else:
            return self.purl
    
    def __process(self):
        bits = self.split()
        for bit in bits:
            if not bit:
                continue
            if bit.startswith('('):
                self.targs += 1
                st = bit.find('<') + 1
                en = bit.find('>')
                if st and en:
                    name = bit[st:en]
                else:
                    raise ApplicationUrlException('Regular expression for urls requires a keyworld. %s does not have one.' % bit)             
                bit  = '%(' + name + ')s'
                self.names.append(name)
            self.breadcrumbs.append(bit)
            self.purl  += '%s/' % bit

    def __add__(self, other):
        if not isinstance(other,self.__class__):
            raise ValueError
        res = copy.deepcopy(self)
        res.url  = '%s%s' % (res.url,other.url)
        res.purl = '%s%s' % (res.purl,other.purl)
        res.targs += other.targs
        res.nargs += other.nargs
        res.names.extend(other.names)
        return res
        
        