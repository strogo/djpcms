

def quote(s):
    """
    Ensure that primary key values do not confuse the admin URLs by escaping
    any '/', '_' and ':' characters. Similar to urllib.quote, except that the
    quoting is slightly different so that it doesn't get automatically
    unquoted by the Web browser.
    """
    if type(s) != type(''):
        return s
    res = list(s)
    for i in range(len(res)):
        c = res[i]
        if c in ':/_':
            res[i] = '_%02X' % ord(c)
    return ''.join(res)