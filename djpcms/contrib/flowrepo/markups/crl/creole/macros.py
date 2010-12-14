
import creole

MACRO_HOLDER = {}

def addmacro(func, name = None):
    global MACRO_HOLDER
    name = name or func.__name__
    if not MACRO_HOLDER.has_key(name):
        MACRO_HOLDER[name] = func
        

def get(name):
    global MACRO_HOLDER
    return MACRO_HOLDER.get(name,None)


def dbimage(body, *args, **kwargs):
    '''
    Database image macro
    '''
    from flowrepo.models import Image
    body = body.replace(' ','')
    try:
        elem = Image.objects.get(name = body)
    except:
        return u''
    return u''
addmacro(dbimage)


def quote(body, *args, **kwargs):
    html = ['<blockquote>',
            '<div class="body-quote">',
            '%s' % body,
            '</div>']
    if len(args) == 1:
        html.append('<div class="cite-quote">%s</div>' % args[0])
    html.append('</blockquote>')
    return '\n'.join(html)
addmacro(quote)


def image(body, *args, **kwargs):
    '''
    Nice macro to include images from the database.
    @param body: the slug field of flowrepo.Image
    @return: img html tag
    
    Usage:
        <<image|some-photo>>
    '''
    from flowrepo.utils import htmlattr
    from flowrepo.models import Image
    try:
        img = Image.objects.get(slug = body)
    except:
        return u''
    kwargs['title'] = kwargs.pop('title',None) or img.description or img.name
    kwargs['alt']   = kwargs.pop('alt',None) or img.name
    kwargs['src']   = img.url
    att = htmlattr(kwargs)
    return '<a href="%s" title="%s"><img%s/></a>' % (img.url,img.name,att.flat())
addmacro(image)

def yesno(body):
    return '<span class="%s-tick"></span>' % body
addmacro(yesno)


def title(body, *args, **kwargs):
    '''
    Title
    '''
    titleclass = 'flow-title'
    size = kwargs.get('size',1)
    tag  = 'h%s' % size
    url  = kwargs.get('url',None)
    if url:
        body = '<a href="%s">%s</a>' % (url,body)
    return '<%s class="%s">%s</%s>' % (tag,titleclass,body,tag)
    #return creole.DocNode(content = content)
addmacro(title)