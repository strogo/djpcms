import sys
import logging

from djpcms import sites
from djpcms.core.models import ModelInterface
from djpcms.template import escape
from djpcms.core.exceptions import BlockOutOfBound
from djpcms.core.permissions import has_permission, get_view_permission
from djpcms.plugins import get_wrapper, default_content_wrapper, get_plugin
import djpcms.contrib.flowrepo.markups as markuplib


def block_htmlid(pageid, block):
    '''HTML id for a block container. Used throughout the library.'''
    return 'djpcms-block-{0}-{1}'.format(pageid,block)


class PageInterface(ModelInterface):
    '''Page object interface'''
    
    def numblocks(self):
        raise NotImplementedError
    
    def create_template(self, name, templ):
        raise NotImplementedError
    
    def set_template(self, template):
        self.inner_template = template
        self.save()
        
    def get_template(self, djp = None):
        '''Returns the name of the ``HTML`` template file for the page.
If not specified we get the template of the :attr:`parent` page.'''
        if not self.template:
            if self.parent:
                return self.parent.get_template(djp)
            else:
                sett = sites.settings if not djp else djp.settings
                return sett.DEFAULT_TEMPLATE_NAME
        else:
            return self.template
    
    def add_plugin(self, p, block = 0):
        '''Add a plugin to a block'''
        b = self.get_block(block)
        try:
            name = p.name
        except:
            name = p
        b.plugin_name = name
        b.save()
        return b 
    
    def get_block(self, block, position = None):
        nb = self.numblocks()
        if block < 0 or block >= nb:
            raise BlockOutOfBound('Page has {0} blocks'.format(nb))
        return self._get_block(block, position)
    
    # INTERNALS
    
    def _get_block(self, block, position):
        raise NotImplementedError
    
    def get_level(self):
        try:
            url = self.url
            if url.startswith('/'):
                url = url[1:]
            if url.endswith('/'):
                url = url[:-1]
            if url:
                bits  = url.split('/')
                level = len(bits)
            else:
                level = 0
        except:
            level = 1
        return level
    

class BlockInterface(object):
    '''Content Block Interface'''
    logger  = logging.getLogger('BlockContent')
    
    def render(self, djp, plugin = None, wrapper = None):
        '''Render the plugin in the content block
This function call the plugin render function and wrap the resulting HTML
with the wrapper callable.'''
        html = ''
        try:
            plugin  = plugin or self.plugin
            wrapper = wrapper or self.wrapper
            if plugin:
                if has_permission(djp.request.user,get_view_permission(self), self):
                    djp.media += plugin.media
                    html = plugin(djp, self.arguments, wrapper = wrapper)
        except Exception, e:
            if getattr(djp.settings,'TESTING',False):
                raise
            exc_info = sys.exc_info()
            self.logger.error('%s - block %s -- %s' % (plugin,self,e),
                exc_info=exc_info,
                extra={'request':djp.request}
            )
            if djp.request.user.is_superuser:
                html = escape(u'%s' % e)
        
        if html:
            return wrapper(djp, self, html)
        else:
            return html
        
    def htmlid(self):
        return 'blockcontent-{0}'.format(self)
    
    def pluginid(self, extra = ''):
        p = 'plugin-{0}'.format(self)
        if extra:
            p = '{0}-{1}'.format(p,extra)
        return p
            
    def __unicode__(self):
        return u'%s-%s-%s' % (self.page.id,self.block,self.position)
    
    def __get_plugin(self):
        return get_plugin(self.plugin_name)
    plugin = property(__get_plugin)
        
    def _get_wrapper(self):
        return get_wrapper(self.container_type,default_content_wrapper)
    wrapper = property(_get_wrapper)
    
    def plugin_class(self):
        '''
        utility functions.
        Return the class of the embedded plugin (if available)
        otherwise it returns Null
        '''
        if self.plugin:
            return self.plugin.__class__
        else:
            return None
    
    
class MarkupMixin(object):
    
    def htmlbody(self):
        text = self.body
        if not text:
            return ''
        mkp = markuplib.get(self.markup)
        if mkp:
            handler = mkp.get('handler')
            text = handler(text)
            text = mark_safe(force_str(text))
        return text
    
    