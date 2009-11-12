import creole
import creole2html


Parser = creole.Parser


class HtmlEmitter(creole2html.HtmlEmitter):
    
    def __init__(self, document):
        creole2html.HtmlEmitter.__init__(self,document)

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
        
    def macro_emit(self, node):
        '''
        Handle a macro
        '''
        target = node.content
        if node.children:
            inside = self.emit_children(node)
        else:
            inside = self.html_escape(target)
        return u'MACRO %s NOT AVAILABLE' % target
    
    


MACRO_HOLDER = {}
        
        