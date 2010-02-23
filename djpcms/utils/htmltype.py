from django.utils.safestring import mark_safe

class htmldoc(object):
    
    def __init__(self, name, html, vimg, slash = ""):
        self.name = name
        self.html = mark_safe(html)
        self.vimg = vimg
        self.slash = slash
        
    def __unicode__(self):
        return u'%s' % self.name
    
    def _validatorsrc(self, extra = ''):
        src = '#'
        if self.vimg:
            src= '''http://www.w3.org/Icons/%s%s.png''' % (self.vimg,extra)
        src = '''<img alt="Valid %s" src="%s"%s>''' % (self.name,src,self.slash)
        return mark_safe('''<a href="http://validator.w3.org/check?uri=referer">%s</a>''' % src)
    
    def bluevalidator(self):
        return self._validatorsrc('-blue')
    
    def validator(self):
        return self._validatorsrc()


def get(code = None):
    global _htmldict, htmldefault
    code = code or htmldefault
    d = _htmldict.get(code,None)
    if not d:
        d = _htmldict.get(htmldefault)
    return d


htmldefault = 4

htmldocs = (
            (1, 
             htmldoc('HTML 4.01',
                     """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
                        "http://www.w3.org/TR/html4/strict.dtd">""",
                     "valid-html401")),
            (2, 
             htmldoc('HTML 4.01 Transitional',
                     """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
                        "http://www.w3.org/TR/html4/loose.dtd">""",
                     "valid-html401")),
            (3, 
             htmldoc('XHTML 1.0 Strict',
                     """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">""",
                     "valid-xhtml10",
                     "/")),
            (4, 
             htmldoc('XHTML 1.0 Transitional',
                     """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">""",
                     "valid-xhtml10",
                     "/")),
            (5, 
             htmldoc('HTML5',
                     """<!DOCTYPE html>""",
                     None)),
            )

_htmldict = dict(htmldocs)

