from django.utils.encoding import iri_to_uri
import copy

class RegExUrl(object):
    '''
    Helper class for url regular expression manipulation
    @param url: regular expression string
    @param split: if True the url will be split using '/' as separator  
    '''
    def __init__(self, url = None, split = True):
        self.url    = str(url or '')
        self.purl   = ''
        self.targs  = 0
        self.nargs  = 0
        self._split = split
        self.breadcrumbs = []
        if self.url:
            self.__process()
            self.url  = '%s/' % self.url
        
    def __len__(self):
        return len(self.url)
    
    def split(self):
        if self._split:
            return self.url.split('/')
        else:
            return ['%s' % self.url]
        
    def __str__(self):
        return '^%s$' % self.url

    def get_url(self, request, **kwargs):
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
                    self.nargs += 1
                    name   = 'arg_no_key_%s' % nargs
                            
                bit  = '%(' + name + ')s'
            self.breadcrumbs.append(bit)
            self.purl  += '%s/' % bit

    def __add__(self, other):
        if not isinstance(other,self.__class__):
            raise ValueError
        res = copy.copy(self)
        res.url  = '%s%s' % (res.url,other.url)
        res.purl = '%s%s' % (res.purl,other.purl)
        res.targs += other.targs
        res.nargs += other.nargs
        return res
        
        