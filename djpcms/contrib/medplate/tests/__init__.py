from djpcms import test
from djpcms.contrib.medplate import CssContext, defaults, base_context
from djpcms.contrib.medplate.management.commands.style import Command


class TestCss(test.TestCase):
        
    def testTemplate(self):
        c = CssContext('test',tag='div.test',data={'color':'#333'},defaults=defaults)
        self.assertEqual(c['tag'],'div.test')
        html = c.render()
        self.assertTrue('color: #333;' in html)
        self.assertTrue('background: {background};'.format(**defaults) in html)
        
    def testBox(self):
        box = base_context.box
        html = box.render()
        self.assertTrue('div.djpcms-html-box div.hd' in html)
        
