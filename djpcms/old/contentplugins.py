'''
Model responsible for handling html rendering of plugins
This module is closely associated with the views module
'''
from django.conf import settings
from django.db.models.base import ModelBase
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.encoding import force_unicode
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template import loader

from djpcms.plugins import content_wrapper_tuple, CONTENT_WRAP_HANDLERS, get_plugin
from djpcms.settings import CONTENT_INLINE_EDITING, HTML_CLASSES
from djpcms.html import formlet, submit
from djpcms.utils.ajax import jhtmls
from djpcms.utils import requestwrap

from page import Page
from apppage import AppPage
from base import current_app_label


__all__ = ['BlockContent',
           'AppBlockContent',
           'DJPplugin',
           'all_plugins']


class ContentBlockError(Exception):
    pass


_all_plugins = [('','---------------------')]
#_all_plugins = []
_plugin_dictionary = {}


def all_plugins():
    global _all_plugins
    return _all_plugins
         

class BlockContentManager(models.Manager):
    '''
    BlockContent manager
    '''
    def for_page_block(self, page, block):
        '''
        Get contentblocks for a given page and block
        @param page: instance of a page model
        @param block: integer indicating the block number
        @return: a queryset  
        '''
        blockcontents = list(self.filter(page = page, block = block))
        create = False
        pos = None

        # No contents, create an empty one
        if not blockcontents:
            create = True
            pos    = 0
        # Last content has a plugin. Add another block
        elif blockcontents[-1].plugin_name:
            create = True
            pos = blockcontents[-1].position + 1
            
        if create:
            bc =self.model(page = page, block = block, position = pos)
            bc.save()
            
        return self.filter(page = page, block = block)
    
    def plugin_content_from_name(self, name):
        global _plugin_dictionary
        model = _plugin_dictionary.get(name,None)
        if model:
            return ContentType.objects.get_for_model(model)
        else:
            return None
        
    def delete_and_sort(self, instance):
        '''
        This function delete from database a blockcontent instance.
        Actually it only deletes it if there are more than one contents in the block
        otherwise it only delete the embedded plugin
        @param instance: instance of BlockContent 
        '''
        if instance and instance.plugin:
            blockcontents = self.for_page_block(instance.page, instance.block)
            
            if blockcontents.count() == 1:
                b = blockcontents[0]
                if b != instance:
                    raise ContentBlockError("Critical error in deleting contentblock")
                b.delete_plugin()
            elif blockcontents.count() > 1:
                pos = 0
                for b in blockcontents:
                    if b == instance:
                        b.delete()
                    elif b.position != pos:
                        b.position = pos
                        b.save()
                        pos += 1
            else:
                raise ContentBlockError("Critical error in deleting contentblock. No Contentblock found")
            
            return True
        else:
            return False




class BlockContentBase(models.Model):
    '''
    A block content object is responsible for mantaining
    relationship between html plugins and their position in page
    '''
    block          = models.PositiveSmallIntegerField(_("block"), editable = False)
    position       = models.PositiveIntegerField(_("position"), blank=True, editable=False, default = 0)
    plugin_name    = models.CharField(blank = True, max_length = 100)
    arguments      = models.TextField(blank = True)
    container_type = models.PositiveSmallIntegerField(choices = content_wrapper_tuple(),
                                                      default = 0,
                                                      verbose_name=_('container'))
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return '%s-%s-%s' % (self.page.id,self.block,self.position)
    
    def htmlid(self):
        return u'blockcontent-%s' % self
    
    def pluginid(self):
        return u'plugin-%s' % self
    
    def __get_plugin(self):
        return get_plugin(self.plugin_name)
    plugin = property(__get_plugin)
        
        
    def wrapper(self):
        ct = int(self.container_type)
        return CONTENT_WRAP_HANDLERS[ct]
    
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
        
    def changeform(self, djp):
        f = self.plugin.get_form(djp)
        #, prefix = 'cf_%s' % self.pluginid())
        return formlet(form = f, layout = 'onecolumn',
                       submit = submit(value = 'Change',
                                       name  = 'change_plugin_content'))
    
    def render(self, djp):
        '''
        @param cl: instance of djpcms.views.baseview.ResponseBase
         
        Render the plugin.
        This function is called when the plugin needs to be rendered
        This function call the plugin render function passing three arguments
        '''
        plugin = self.plugin
        if plugin:
            #prefix  = 'bd_%s' % self.pluginid()
            prefix = None
            djp    = djp(wrapper = self.wrapper().handler, prefix = prefix)
            return plugin(djp,self.arguments)
        else:
            return u''
    
    def change_plugin_content(self, request):
        '''
        Handle a POST request when changing app_page
        '''
        f = self.changeform(request = request)
        if f.is_valid():
            self.plugin = f.save()
            return jhtmls(identifier = '#preview-%s' % self.htmlid(),
                          html = self.render(request = request)) 
        else:
            return f.jerrors
    
    
class BlockContent(BlockContentBase):
    page           = models.ForeignKey(Page, verbose_name=_("page"), editable = False, related_name = 'blockcontents')
    
    objects = BlockContentManager()
    
    class Meta:
        verbose_name = 'Block content for Page'
        verbose_name_plural = 'Block contents for Pages'
        app_label = current_app_label
        unique_together = (('page','block','position'),)
        ordering  = ('page','block','position',)
    
    
class AppBlockContent(BlockContentBase):
    page           = models.ForeignKey(AppPage, verbose_name=_("page"), editable = False, related_name = 'blockcontents')
    
    objects = BlockContentManager()
    
    class Meta:
        verbose_name = 'Block contents for AppPage'
        verbose_name_plural = 'Block contents for AppPages'
        app_label = current_app_label
        unique_together = (('page','block','position'),)
        ordering  = ('page','block','position',)
    
    
class PluginModelBase(ModelBase):
    """
    Metaclass for all plugins.
    
    Plugin model must be default constructable.
    Therefore they can be constructed by simple doing
        p = SomePlugin()
        p.save()
    """
    def __new__(cls, name, bases, attrs):
        global _all_plugins, _plugin_dictionary
        new_class = super(PluginModelBase, cls).__new__(cls, name, bases, attrs)
        if new_class._meta.abstract:
            return new_class
        
        found = False
        for base in bases:
            if base.__name__ == "DJPplugin":
                found = True
                break
        if found:
            if new_class._meta.db_table.startswith("%s_" % new_class._meta.app_label):
                table = "djpplugin_" + new_class._meta.db_table.split("%s_" % new_class._meta.app_label, 1)[1]
                new_class._meta.db_table = table
                #if new_class.add_to_list:
                #    register_djpplugin(new_class) 
        return new_class 
    
    
    
class DJPplugin(models.Model):
    __metaclass__ = PluginModelBase
    '''
    Base class for all plugins.
    Each plugin must:
        1 - implements the __unicode__ function which renders the plugin
        2 - implements the changeform function which render plugin editing panel
    '''
    add_to_list   = True
    last_modified = models.DateTimeField(auto_now = True, editable = False)
    title         = models.CharField(max_length = 100, blank = True)
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return force_unicode(self._meta.verbose_name)
        
    def render(self, djp, **kwargs):
        '''
        Function called to render the plugin
        '''
        if settings.DEBUG:
            return u'render function not implemented for this plugin'
        else:
            return u''
        
    def changeform(self, request = None, prefix = None):
        '''
        Form for editing the plugin in a contentblock
        By default it is empty.
        Plugins are responsible for the implementation of their changeform.
        @return html unicode if possible
        '''
        return u''
        
    def handlerequest(self, data, key):
        pass
    

