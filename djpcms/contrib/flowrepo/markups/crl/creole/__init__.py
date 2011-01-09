import creole
import creole2html
import macros

from djpcms import sites

# Try to import pygments. If available, use it to render code
try:
    import pygments
    from pygments import highlight
    from pygments.lexers import guess_lexer, get_lexer_by_name
    from pygments.formatters import HtmlFormatter
except:
    pygments = None


Parser = creole.Parser


class HtmlEmitter(creole2html.HtmlEmitter):
    '''
    Create a new HTML Emitter
    '''
    def __init__(self, document):
        creole2html.HtmlEmitter.__init__(self,document)

    def paragraph_emit(self, node):
        body = self.emit_children(node)
        if body:
            return u'<p>%s</p>\n' % body
        else:
            return ''
    
    def link_emit(self, node):
        target = node.content
        if node.children:
            inside = self.emit_children(node)
        else:
            inside = self.html_escape(target)
        m = self.addr_re.match(target)
        if m:
            if m.group('extern_addr'):
                return u'<a href="%s" target="_blank">%s</a>' % (
                    self.attr_escape(target), inside)
            elif m.group('inter_wiki'):
                raise NotImplementedError
        return u'<a href="%s">%s</a>' % (
            self.attr_escape(target), inside)
        
    def preformatted_emit(self, node):
        if pygments:
            return HandleCode(node.content)
        else:
            return u"<pre>%s</pre>" % self.html_escape(node.content)
        
    def header_emit(self, node):
        content = node.content
        return u'<h%d>%s</h%d>\n' % (
            node.level, self.html_escape(content), node.level)
        
    def macro_emit(self, node):
        '''
        Handle a macro
        A macro is defined by the sintax
        <<macroname|body|*args||**kwargs>>
        where body is the main body of the macro and **kwargs
        represents a dictionary of options (comma separated)
        
        Example:
        <<quote|this is a quotation|arg1,arg2||option1=bla,option2=foo>>
        '''
        target = node.content
        macro  = macros.get(target)
        
        if not macro:
            return u'MACRO %s NOT AVAILABLE' % target
        elif node.children:
            inside = self.emit_children(node)
            if inside:
                elems = inside.split('||')
                items = elems[0].split('|')
                inside = items[0]
                args   = tuple(items[1:])
                if len(elems) == 2:
                    kwargs = self.macrooptions(elems[1])
                else:
                    kwargs = {}  
                return macro(inside, *args, **kwargs)
            else:
                return macro(inside)
        else:
            return u''
    
    def macrooptions(self, body):
        kwargs = {}
        opts   = body.replace(' ','').split(',')
        kwargs = {}
        for opt in opts:
            entry = opt.split('=')
            if len(entry) == 2:
                kwargs[str(entry[0])] = entry[1]
        return kwargs
    
    
def HandleCode(code):
    '''
    Pygments handler.
    Check for a hint in the first line. If it finds the lexer use it otherwise
    guess it
    '''
    codes = code.split('\n')
    try:
        language = codes[0]
        lexer = get_lexer_by_name(language, stripall=True)
        code  = '\n'.join(codes[1:])
    except:
        lexer = guess_lexer(code)
    formatter = HtmlFormatter(linenos=getattr(sites.settings,'FLOWREPO_CODE_LINENO',False),
                              cssclass="source")
    result = highlight(code, lexer, formatter)
    return result

    
        