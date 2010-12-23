import unittest
from itertools import izip

from djpcms.utils.collections import OrderedDict
from djpcms.utils.populate import populate


class TestOrderedDict(unittest.TestCase):

    def testInstance(self):
        d = OrderedDict()
        self.assertTrue(isinstance(d,dict))
        
    def testOrderSimple(self):
        d = OrderedDict()
        d['ciao']  = 1
        d['abcbd'] = 2
        d[56]      = 3
        for n,kv in enumerate(d.iteritems(), start = 1):
            self.assertEqual(n,kv[1]) 
    
    def testOrderList(self):
        x = populate('string',300, min = 5, max = 15)
        y = populate('string',300, min = 5, max = 15)
        data = zip(x,y)
        od = OrderedDict(data)
        self.assertEqual(len(od),300)
        for t,v in izip(od.iteritems(),data):
            self.assertEqual(t,v)