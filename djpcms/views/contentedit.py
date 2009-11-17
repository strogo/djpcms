from django import http
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext, loader

from djpcms.settings import HTML_CLASSES, CONTENT_INLINE_EDITING
from djpcms.models import BlockContent, AppBlockContent, Page, AppPage, all_plugins
from djpcms.plugins.wrapper import content_wrapper_tuple
from djpcms.plugins.application import appsite
from djpcms.plugins.wrapper import ContentWrapperHandler
from djpcms.views.appview import EditApp
from djpcms.utils import form_kwargs
from djpcms.utils.ajax import jhtmls
from djpcms.forms import LazyAjaxChoice

    

basecontent = CONTENT_INLINE_EDITING.get('pagecontent', '/content/')

EDIT_BLOCK_TEMPLATES = ["content/edit_block.html",
                        "djpcms/content/edit_block.html"]


class content_view(object):
    '''
    Utility class for creating the editing generator
    '''
    def __init__(self, page):
        if page == AppPage or isinstance(page, AppPage):
            self.blockClass = AppBlockContent
        else:
            self.blockClass = BlockContent
            
    def blockcontents(self, page, b):
        return self.blockClass.objects.for_page_block(page, b)
    
    def __call__(self, request, blockcontents):
        '''
        Return a generator
        '''
        appmodel = appsite.site.for_model(self.blockClass)
        view = appmodel.getapp('main')
        wrapper = EditWrapperHandler()
        for b in blockcontents:
            djp  = view.requestview(request, instance = b)
            djp.wrapper = wrapper
            #djp.prefix  = wrapper.prefix(b)
            yield wrapper.wrap(djp)


class EditWrapperHandler(ContentWrapperHandler):
    '''
    wrapper for editing content
    '''
    form_layout = 'onecolumn'
    
    def prefix(self, instance):
        '''
        prefix for given block
        '''
        return 'bd_%s' % instance.pluginid()
    
    def wrap(self, djp):
        '''
        render a block for content editing
        '''
        form = djp.view.render(djp)
        instance = djp.instance
        c = {'djp':               djp,
             'contentblock':      instance,
             'form':              form,
             'plugin_edit_block': instance.plugin_edit_block(djp)}
        return loader.render_to_string(EDIT_BLOCK_TEMPLATES, c)


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
    container_type = LazyAjaxChoice(choices = content_wrapper_tuple(), label=_('container'))
        
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
        
        
class ChangeContentView(EditApp):
    '''
    View class for managing inline editing of a content block.
    The url is given by the ContentBlocks models
    '''
    _methods = ('post',)
    
    def __init__(self):
        regex = '(?P<pageid>\d+)/(?P<blocknumber>\d+)/(?P<position>\d+)'
        super(ChangeContentView,self).__init__(regex = regex,
                                               parent = None,
                                               name = 'edit_content_block')
            
    def edit_block(self, request):
        return jhtmls(identifier = '#%s' % self.instance.pluginid(),
                      html = self.instance.plugin_edit_block(request))
        
    def ajax__plugin_name(self, djp):
        '''
        Ajax post view function which handle the change of pluging within one html block.
        @param request: django HttpRequest instance
        @return JSON serializable object 
        '''
        form = self.appmodel.get_form(djp)
        if form.is_valid():
            instance = form.save()
            return jhtmls(identifier = '#%s' % instance.pluginid(),
                          html = instance.plugin_edit_block(djp))
        else:
            pass
        
    def ajax__container_type(self, djp):
        return self.ajax__plugin_name(djp)            
        
    def ajax__delete_plugin(self, djp):
        '''
        Here we delete the BlockContent.
        Deletion only happens when the blockcontent instance has
        a plugin.
        '''
        if BlockContent.objects.delete_and_sort(self.instance):
            pass
        else:
            pass
    
    def ajax__change_plugin_content(self, djp):
        '''
        Ajax view called when changing the content plugin values.
        The instance.plugin object is maintained but its fields may change
        
        @param request: django HttpRequest instance
        @return JSON serializable object 
        '''
        b = self.instance
        form = b.changeform(request = request)
        if form.is_valid():
            b.plugin = form.save()
            cl = self.requestview(request)
            return jhtmls(identifier = '#preview-%s' % b.htmlid(),
                          html = b.render(cl)) 
        else:
            return form.jerrors
        #return self.instance.change_plugin_content(request)
    
    
    def default_ajax_view(self, djp):
        '''
        Ajax view called when changing the plugin values
        '''
        return self.instance.change_plugin(request, self.ajax_key)
        
    def has_permission(self, request):
        if request.user.is_authenticated():
            return True
        else:
            return False
        

class ContentSite(appsite.ModelApplication):
    baseurl   = '%spage/' % basecontent
    pagemodel = Page
    form      = ContentBlockForm
    
    main      = ChangeContentView()
    
    def objectbits(self, obj):
        return {'pageid': obj.page.id,
                'blocknumber': obj.block,
                'position': obj.position}
        
    def get_object(self, pageid = 1, blocknumber = 1, position = 1):
        '''
        Override superclass function.
        This function get the information needed for performing in-line editing.
        @param request: django HttpRequest instance
        @param pageid:  a page id (a string to be converted into an integer)
        @param blocknumber:  block number within the page (a string to be converted into an integer)
        @param position:  position number within the block (a string to be converted into an integer)
        @return None
        '''
        pageid      = int(pageid)
        blocknumber = int(blocknumber)
        position    = int(position)
        page        = self.pagemodel.objects.get(pk = pageid)
        blocks      = self.model.objects.filter(page = page)
        nblocks     = page.numblocks()
        if blocknumber >= nblocks:
            raise http.Http404('Block number too high for current page')
        cb     = blocks.count()
    
        # Create new blocks if necessary
        for bn in range(cb,nblocks):
            b = self.model(page = page, block = bn)
            b.save()
    
        try:
            instance = self.model.objects.get(page = page, block = blocknumber, position = position)
        except:
            raise http.Http404('Position %s not available in content block %s' % (position,blocknumber))
        
        return instance
    
     
class AppContentSite(ContentSite):
    baseurl   = '%sapp/' % basecontent 
    pagemodel = AppPage
    form      = AppContentBlockForm
    
    main      = ChangeContentView()
    
    
    
if appsite.site.editavailable:
    appsite.site.register(BlockContent,ContentSite,False)
    appsite.site.register(AppBlockContent,AppContentSite,False)
    
