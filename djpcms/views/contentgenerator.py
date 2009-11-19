from django import forms
from django.forms.formsets import formset_factory
from django.template import RequestContext, loader
from django.utils.safestring import mark_safe

from djpcms.settings import HTML_CLASSES
from djpcms.djutils import UnicodeObject


class BlockContentGen(UnicodeObject):
    '''
    Block Content Generator.
    This class is responsible for generating contents within a 'block'.
    A page is associated with a given url and a page has a certain number
    of blocks depending on the template chosen for the pages: anything between 1 and 10 is highly possible.
    Within each block there may be one or more contents.
    
    The edit mode block elements are rendered using the EDIT_BLOCK_TEMPLATES templates (see at top of file)
    '''
    def __init__(self, djp, b):
        '''
        Initialize
        @param cl:      instance of djpcms.views.baseview.ResponseBase
        @param b:       integer indicating the block number in the page
        @param page:    instance of Page or AppPage
        '''
        from djpcms.views.contentedit import content_view
        self.djp     = djp
        self.page    = djp.page
        self.view    = djp.view
        self.request = djp.request
        self.b       = b
        self.ecv     = content_view(self.page)
        
    def render(self):
        '''
        Render the Block.
        @return: HTML safe unicode for the block
        '''
        html = [u'<div id="%s" class="djpcms-block">' % self.htmlid()]
        for ht in self.blocks():
            html.append(ht)
        html.append(u'%s</div>' % self.empty())
        return mark_safe(u'\n'.join(html))
    
    def __unicode__(self):
        return self.render()
    
    def htmlid(self):
        return 'djpcms-block-%s-%s' % (self.page.id,self.b)
    
    def blocks(self):
        '''
        Function called within a template for generating all contents
        within a block.
        This function produce HTML only if self.view is based on a database Page
        object. Otherwise it does nothing.
        '''
        blockcontents = self.ecv.blockcontents(self.page, self.b)
        if self.view.editurl:
            return self.ecv(self.request, blockcontents)
        else:
            return self._blocks(blockcontents)
        
    def _blocks(self, blockcontents):
        '''
        Implementation of self.blocks when we are not in editing mode.
        Displaying the actual content of the block
        '''
        for b in blockcontents:
            wrapper = b.wrapper()
            yield wrapper.wrap(self.djp, b)

    def empty(self):
        return '&nbsp;'

