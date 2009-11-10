'''
Wiki Creole Markup

@requires: creoleparser (shipped with djpcms so no need to instal it)
@requires: genshi (must be installed)
'''
try:
    import genshi.builder as bldr
    from genshi.core import Markup
    try:
        import creoleparser
    except ImportError:
        import sys
        sys.path.append('../externals')
    from creoleparser import Parser, create_dialect, creole11_base, parse_args

    def wrap_html(text):
        return Markup(text)   
             
    def macro_func(macro_name, arg_string, body, isblock, environ):
        global _macros
        func = _macros.get(macro_name,None)
        if func:
            args, kwargs = parse_args(arg_string)
            return func(body,*args,**kwargs)
        else:
            return wrap_html("Macro %s not available" % macro_name)

    def addmacro(name, func = None):
        global _macro
        if func is None:
            func = name
            name = func.__name__
        if not _macros.has_key(name):
            _macros[name] = func

    text2html = Parser(dialect=create_dialect(creole11_base, macro_func=macro_func), method='html')
    
    def quote(body, **kwargs):
        '''
        Macro for creating quotation
        '''
        bits = body.split('|')
        html = ['<blockquote>',
                '<div class="body-quote">',
                '%s' % bits[0],
                '</div>']
        if len(bits) > 1:
            html.append('<div class="cite-quote">%s</div>' % bits[1])
        html.append('</blockquote>')
        return wrap_html('\n'.join(html))
    addmacro(quote)

    available = True
except ImportError:
    available = False


_macros = {}
