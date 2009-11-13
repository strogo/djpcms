from django import forms
from django.forms.formsets import formset_factory
from django.template import RequestContext, loader
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from djpcms.settings import HTML_CLASSES
from djpcms.djutils import UnicodeObject
from djpcms.models import BlockContent, AppBlockContent, AppPage, all_plugins
from djpcms.plugins.wrapper import content_wrapper_tuple
from djpcms.djutils.fields import LazyChoiceField


EDIT_BLOCK_TEMPLATES = ["content/edit_block.html",
                        "djpcms/content/edit_block.html"]


class LazyAjaxChoice(LazyChoiceField):
    
    def __init__(self, *args, **kwargs):
        super(LazyAjaxChoice,self).__init__(*args, **kwargs)
        
    def widget_attrs(self, widget):
        return {'class': HTML_CLASSES.ajax}

class PluginChoice(forms.ChoiceField):
    
    def __init__(self, *args, **kwargs):
        super(PluginChoice,self).__init__(*args, **kwargs)
        
    def widget_attrs(self, widget):
        return {'class': HTML_CLASSES.ajax}
    
    def clean(self, value):
        '''
        Overried default value to return a Content Type object
        '''
        name = super(PluginChoice,self).clean(value)
        value = BlockContent.objects.plugin_content_from_name(name)
        if not value:
            raise forms.ValidationError('%s not a plugin object' % name)
        return value
    

class ContentBlockFormBase(forms.ModelForm):
    '''
    Content Block Change form
    
    This Model form is used to change the plug-in within
    for a given BlockContent instance.
    '''
    # This is a subclass of forms.ChoiceField with the class attribute
    # set to ajax.
    plugin_name    = PluginChoice(label = _('content'), choices = all_plugins())
    container_type = LazyAjaxChoice(choices = content_wrapper_tuple(),
                                    label=_('container'))
        
    def __init__(self, instance = None, initial = None, **kwargs):
        '''
        @param instance: must be an instance of BlockContent not Null
        '''
        if not instance:
            raise ValueError('No content block available')
        
        if instance.plugin:
            initial = initial or {}
            mc = instance.plugin_class()
            initial['plugin_name'] = unicode(mc.__name__) 
            
        super(ContentBlockFormBase,self).__init__(instance = instance,
                                              initial = initial,
                                              **kwargs)
        # Hack the field ordering
        self.fields.keyOrder = ['plugin_name', 'container_type']
        
    def save(self, *args, **kwargs):
        pt = self.cleaned_data.pop('plugin_name')
        instance = self.instance
        if not (instance.plugin and pt == instance.plugin_name):
            if instance.plugin:
                instance.plugin.delete()
                delattr(self.instance,'_plugin_cache')
            plugin_instance = pt.model_class()()
            plugin_instance.save()
            self.instance.plugin_name = pt
            self.instance.object_id   = plugin_instance.pk
        return super(ContentBlockFormBase,self).save(*args,**kwargs)

class ContentBlockForm(ContentBlockFormBase):
    '''
    Page ContentBlock Form
    '''
    def __init__(self,*args,**kwargs):
        super(ContentBlockForm,self).__init__(*args,**kwargs)
    class Meta:
        model = BlockContent
        
class AppContentBlockForm(ContentBlockFormBase):
    '''
    AppPage ContentBlock Form
    '''
    def __init__(self,*args,**kwargs):
        super(AppContentBlockForm,self).__init__(*args,**kwargs)
    class Meta:
        model = AppBlockContent





class BlockContentGen(UnicodeObject):
    '''
    Block Content Generator.
    This class is responsible for generating contents within a 'block'.
    A page is associated with a given url and a page has a certain number
    of blocks depending on the template chosen for the pages: anything between 1 and 10 is highly possible.
    Within each block there may be one or more contents.
    
    The edit mode block elements are rendered using the EDIT_BLOCK_TEMPLATES templates (see at top of file)
    '''
    def __init__(self, cl, b):
        '''
        Initialize
        @param cl:      instance of djpcms.views.baseview.ResponseBase
        @param b:       integer indicating the block number in the page
        @param page:    instance of Page or AppPage
        '''
        self.cl      = cl
        self.page    = cl.page
        self.view    = cl.view
        self.request = cl.request
        if isinstance(cl.page, AppPage):
            self.isapp      = True
            self.blockClass = AppBlockContent
            self.form       = AppContentBlockForm
        else:
            self.isapp      = False
            self.blockClass = BlockContent
            self.form       = ContentBlockForm
        self.b       = b
        
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
        return self.htmlid()
    
    def htmlid(self):
        return 'djpcms-block-%s-%s' % (self.page.id,self.b)
    
    def blocks(self):
        '''
        Function called within a template for generating all contents
        within a block.
        This function produce HTML only if self.view is based on a database Page
        object. Otherwise it does nothing.
        '''
        blockcontents = self.blockClass.objects.for_page_block(self.page, self.b)
        if self.view.editurl:
            return self._editblocks(blockcontents)
        else:
            return self._blocks(blockcontents)
        
    def _blocks(self, blockcontents):
        '''
        Implementation of self.blocks when we are not in editing mode.
        Displaying the actual content of the block
        '''
        for b in blockcontents:
            wrapper = b.wrapper()
            plugin  = b.plugin
            if not plugin:
                continue
            # Return a wrapped plugin html
            yield wrapper.wrap(b, self.cl)
        return

    def _editblocks(self, blockcontents):
        '''
        Equivalent to self._blocks but in editing mode
        '''
        for b in blockcontents:
            c = {'cl': self.cl,
                 'contentblock': b,
                 'form': self.form(instance = b),
                 'plugin_edit_block': b.plugin_edit_block(self.cl)}
            yield loader.render_to_string(EDIT_BLOCK_TEMPLATES,
                                          context_instance = RequestContext(self.request,c))
        return

    def empty(self):
        return '&nbsp;'

