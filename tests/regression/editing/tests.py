import json
from djpcms import test
from djpcms.plugins.text import Text 


class Editing(test.TestCase):
    
    def setUp(self):
        super(Editing,self).setUp()
        p = self.get()['page']
        p.set_template(p.create_template('thre-columns',
                                         '{{ content0 }} {{ content1 }} {{ content2 }}',
                                         'left,center,right'))
        for pr in range(0,5):
            p.add_plugin(Text,0)
            p.add_plugin(Text,1)
            p.add_plugin(Text,2)
    
    def postdata(self):
        return {self.sites.settings.HTML_CLASSES.post_view_key:'rearrange'}
    
    def geturl(self, block):
        return '{0}{1}/{2}/{3}/'.format(self.sites.settings.CONTENT_INLINE_EDITING['pagecontent'],
                                          block.page.id,
                                          block.block,
                                          block.position)
        
    def _getcontent(self, block, toblock):
        '''Do as jQuery does'''
        data  = self.postdata()
        if toblock.position:
            if toblock.position <= block.position:
                toblockp = self.get_block(toblock.block,toblock.position-1)
            else:
                toblockp = toblock
            data['previous'] = toblockp.htmlid()
        else:
            data['next'] = toblock.htmlid()
        self.assertTrue(self.login())
        url = self.geturl(block)
        res = self.post(url, data = data, response = True, ajax = True)
        return json.loads(res.content)
        
    def get_block(self, blocknum, position):
        '''Get a content block from page and perform sanity check'''
        p = self.get()['page']
        block = p.get_block(blocknum,position)
        self.assertEqual(block.block,blocknum)
        self.assertEqual(block.position,position)
        return block
        
    def testLayout(self):
        p = self.get()['page']
        self.assertEqual(p.numblocks(),3)
    
    def testRearrangeSame(self):
        block = self.get_block(2,3)
        content = self._getcontent(block,block)
        self.assertEqual(content['header'],'empty')
        
    def testRearrangeSame0(self):
        block = self.get_block(1,0)
        content = self._getcontent(block,block)
        self.assertEqual(content['header'],'empty')
        
    def testRearrange3to1SameBlock(self):
        block = self.get_block(2,3)
        toblock = self.get_block(2,1)
        content = self._getcontent(block,toblock)
        self.assertEqual(content['header'],'attribute')
        data = content['body']
        ids  = dict(((el['selector'],el['value']) for el in data))
        self.assertTrue(ids['#'+block.htmlid()],toblock.htmlid())
        self.assertTrue(ids['#'+toblock.htmlid()],block.htmlid())
        
    def testRearrange3to0SameBlock(self):
        block = self.get_block(2,3)
        toblock = self.get_block(2,0)
        content = self._getcontent(block,toblock)
        self.assertEqual(content['header'],'attribute')
        data = content['body']
        ids  = dict(((el['selector'],el['value']) for el in data))
        self.assertTrue(ids['#'+block.htmlid()],toblock.htmlid())
        self.assertTrue(ids['#'+toblock.htmlid()],block.htmlid())
        
    def testRearrange1to4SameBlock(self):
        block = self.get_block(2,1)
        toblock = self.get_block(2,4)
        content = self._getcontent(block,toblock)
        self.assertEqual(content['header'],'attribute')
        data = content['body']
        ids  = dict(((el['selector'],el['value']) for el in data))
        self.assertTrue(ids['#'+block.htmlid()],toblock.htmlid())
        self.assertTrue(ids['#'+toblock.htmlid()],block.htmlid())

    def testRearrangeDifferentBlock(self):
        block = self.get_block(2,3)
        toblock = self.get_block(0,1)
        content = self._getcontent(block,toblock)
        self.assertEqual(content['header'],'attribute')
        data = content['body']
