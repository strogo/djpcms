from djpcms.test import TestCase
from djpcms.contrib.flowrepo import markups

__all__ = ['markup']


text_rst = '''
.. math::

    x^2 + y^2
'''

simple_rst = '''
A title
==============

blab bla
'''


class markup(TestCase):
    
    def _testRstSimple(self):
        rst = markups.get('rst')
        if rst:
            r = rst['handler'](simple_rst)
            self.assertTrue('A title' in r)
        
    def _testRstMath(self):
        rst = markups.get('rst')
        if rst:
            r = rst['handler'](text_rst)
            pass
