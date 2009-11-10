

def datatourl(url,data):
    ps = []
    for k,v in data.items():
        v = v or ''
        ps.append('%s=%s' % (k,v))
    p = '&'.join(ps)
    return '%s?%s' % (url,p)


def listtohtml(li, sep = ', ', lastsep = None):
    if not lastsep:
        return sep.join(li)
    else:
        n = len(li)
        if not n:
            return ''
        if n == 1:
            return li[0]
        else:
            lim = li[:n-1]
            r = [sep.join(lim),li[n-1]]
            return lastsep.join(r)