from base import link, button, compactTag, get_ajax

def ajaxlink(url, inner = None, title = None):
    return link(url = url, inner = inner, cn = get_ajax().ajax).attr(title = title)

def ajaxeditlink(url, inner = None, title = 'edit', func = None):
    cn = '%s %s' % (get_ajax().ajax,get_ajax().edit)
    return link(url = url, inner = inner, cn = cn).attr(title = title, name = func)

def ajaxdeletelink(url, inner = None, title = 'delete', func = None):
    cn = '%s %s' % (get_ajax().ajax,get_ajax().delete)
    return link(url = url, inner = inner, cn = cn).attr(title = title, name = func)

def ajaxbutton(url, inner = None, func = None):
    return button(inner = inner, cn = get_ajax().ajax).attr(name = func, href = url)

def submit(value = 'submit', name = 'submit', **kwargs):
    return compactTag(tag = 'input', **kwargs).attr(value = value, name = name, type = 'submit')            