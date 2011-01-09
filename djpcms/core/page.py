import sys
import logging

from djpcms import sites
from djpcms.core.models import ModelInterface
from djpcms.template import escape
from djpcms.core.exceptions import BlockOutOfBound
from djpcms.permissions import has_permission, get_view_permission


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
        b = self.get_block(0)
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
    
    

class BlockInterface(object):
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