import string

from plasTeX.Renderers import Renderer
from plasTeX.Renderers.XHTML import Renderer



def mathml_equation(node):
    return u'<math xmnls="http://www.w3.org/Math/testsuite/build/mathml3/frameset-full.xhtml">\n%s\n</math>' % ''



class MathMLRenderer(Renderer):
    
    def __init__(self, data = None):
        if data is None:
            data = {}
        super(MathMLRenderer, self).__init__(data = data)
        #self['equation'] = mathml_equation
    
    def default(self, node):
        """ Rendering method for all non-text nodes """
        s = []

        # Handle characters like \&, \$, \%, etc.
        if len(node.nodeName) == 1 and node.nodeName not in string.letters:
            return self.textDefault(node.nodeName)

        # Start tag
        s.append('<%s>' % node.nodeName)

        # See if we have any attributes to render
        if node.hasAttributes():
            s.append('<attributes>')
            for key, value in node.attributes.items():
                # If the key is 'self', don't render it
                # these nodes are the same as the child nodes
                if key == 'self':
                    continue
                s.append('<%s>%s</%s>' % (key, unicode(value), key))
            s.append('</attributes>')

        # Invoke rendering on child nodes
        s.append(unicode(node))

        # End tag
        s.append('</%s>' % node.nodeName)

        return u'\n'.join(s)

    def textDefault(self, node):
        """ Rendering method for all text nodes """
        return node.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

