from django.conf import settings
from django.db.models.base import ModelBase
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.encoding import force_unicode
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template import loader

from djpcms.plugins import content_wrapper_tuple, CONTENT_WRAP_HANDLERS
from djpcms.settings import CONTENT_INLINE_EDITING, HTML_CLASSES
from djpcms.html import formlet, submit
from djpcms.ajax import jhtmls
from djpcms.djutils import requestwrap

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
        elif blockcontents[-1].plugin:
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
    plugin_name    = models.ForeignKey(ContentType, verbose_name=_('plugin name'), null=True, editable = False)
    object_id      = models.PositiveIntegerField(_('object id'), db_index=True, null=True, editable = False)
    plugin         = generic.GenericForeignKey('plugin_name', 'object_id')
    container_type = models.PositiveSmallIntegerField(choices = content_wrapper_tuple(), default = 0, verbose_name=_('container'))
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return '%s-%s-%s-%s' % (self.typenum,self.page.id,self.block,self.position)
    
    def __get_typenum(self):
        return self.page.typenum
    typenum = property(fget = __get_typenum)
    
    def htmlid(self):
        return u'blockcontent-%s' % self
    
    def pluginid(self):
        return u'plugin-%s' % self
    
    def url(self):
        baseurl = CONTENT_INLINE_EDITING.get('pagecontent','/content/')
        return '%s%s/%s/%s/%s/' % (baseurl,self.typenum,self.page.id,self.block,self.position)
        
    def wrapper(self):
        return CONTENT_WRAP_HANDLERS[self.container_type]
    
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
    
    def delete_plugin(self):
        plugin = self.plugin
        self.plugin_name = None
        self.object_id = None
        plugin.delete()
        self.save()
        
    def plugin_edit_block(self, request = None):
        if not self.plugin:
            return u''
        req = requestwrap(self,request)
        return loader.render_to_string('djpcms/content/edit_content_plugin.html', {'contentblock':req,
                                                                                   'css': HTML_CLASSES})
        
    def changeform(self, request = None):
        f = self.plugin.changeform(request = request, prefix = 'cf_%s' % self.pluginid())
        return formlet(form = f,
                       layout = 'onecolumn',
                       submit = submit(value = 'Change',
                                       name  = 'change_plugin_content'))
    
    def render(self, request = None, view = None):
        '''
        Render the plugin.
        This function is called when the plugin needs to be rendered
        This function call the plugin render function passing three arguments
        '''
        return self.plugin.render(request = request,
                                  prefix  = 'bd_%s' % self.pluginid(),
                                  wrapper = self.wrapper().handler,
                                  view    = view)
    
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
        app_label = current_app_label
        unique_together = (('page','block','position'),)
        ordering  = ('page','block','position',)
    
    
class AppBlockContent(BlockContentBase):
    page           = models.ForeignKey(AppPage, verbose_name=_("page"), editable = False, related_name = 'blockcontents')
    
    objects = BlockContentManager()
    
    class Meta:
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
                namep = new_class.__name__
                vname = force_unicode(new_class._meta.verbose_name)
                _all_plugins.append((namep,vname))
                _plugin_dictionary[namep] = new_class 
        return new_class 
    
    
    
class DJPplugin(models.Model):
    __metaclass__ = PluginModelBase
    '''
    Base class for all plugins.
    Each plugin must:
        1 - implements the __unicode__ function which renders the plugin
        2 - implements the changeform function which render plugin editing panel
    '''
    last_modified = models.DateTimeField(auto_now = True, editable = False)
    title         = models.CharField(max_length = 100, blank = True)
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return force_unicode(self._meta.verbose_name)
        
    def render(self, request, prefix, wrapper, **kwargs):
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
    

