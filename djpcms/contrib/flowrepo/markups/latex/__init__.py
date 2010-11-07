# Import renderer from previous code sample

import setenv

try:
    from Renderers.report import Renderer
    from plasTeX.TeX import TeX

    # Instantiate a TeX processor and parse the input text
    tex = TeX()
    tex.ownerDocument.config['files']['split-level'] = -100
    tex.ownerDocument.config['files']['filename'] = 'test.xml'

    def text2html(text):
        text = r'%s' % text
        tex.input(text)
        document = tex.parse()

        # Render the document
        renderer = Renderer()
        renderer.render(document)
except:
    def text2html(text):
        return text
