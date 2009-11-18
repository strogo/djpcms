from django import http
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext, loader

from djpcms.settings import HTML_CLASSES, CONTENT_INLINE_EDITING
from djpcms.models import BlockContent, AppBlockContent, Page, AppPage
from djpcms.utils import form_kwargs
from djpcms.utils.ajax import jhtmls
from djpcms.utils.formjson import form2json
from djpcms.utils.html import form, formlet, submit, htmlcomp
from djpcms.forms import LazyChoiceField, LazyAjaxChoice
from djpcms.plugins import get_plugin, functiongenerator, \
                           ContentWrapperHandler, content_wrapper_tuple
from djpcms.views import appsite, appview

    

basecontent = CONTENT_INLINE_EDITING.get('pagecontent', '/content/')


# Generator of content block in editing mode.
# Only called when we are in editing mode
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
        view = appmodel.getapp('edit')
        wrapper = EditWrapperHandler()
        for b in blockcontents:
            djp  = view.requestview(request, instance = b)
            djp.wrapper = wrapper
            #djp.prefix  = wrapper.prefix(b)
            yield wrapper.wrap(djp)


# Content wrapper in editing mode.
# Only called by content_view (funation above)
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
        view     = djp.view
        instance = djp.instance
        form     = view.render(djp)
        try:
            html     = instance.render(djp)
        except Exception, e:
            html     = u'%s' % e
        delurl   = view.appmodel.deleteurl(djp.request, instance)
        c = {'djp':               djp,
             'form':              form,
             'preview':           html,
             'instance':          djp.instance,
             'deleteurl':         delurl,
             'plugin_preview_id': view.plugin_preview_id(instance)}
        return loader.render_to_string(["content/edit_block.html",
                                        "djpcms/content/edit_block.html"],
                                        c)


class PluginChoice(LazyAjaxChoice):
    
    def __init__(self, *args, **kwargs):
        super(PluginChoice,self).__init__(*args, **kwargs)
    
    def clean(self, value):
        '''
        Overried default value to return a Content Type object
        '''
        name = super(PluginChoice,self).clean(value)
        value = get_plugin(name) 
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
    plugin_name    = PluginChoice(label = _('content'),   choices = functiongenerator, required = False)
    container_type = LazyChoiceField(label=_('container'), choices = content_wrapper_tuple())
        
    def __init__(self, instance = None, **kwargs):
        '''
        @param instance: must be an instance of BlockContent not Null
        '''
        if not instance:
            raise ValueError('No content block available')
        super(ContentBlockFormBase,self).__init__(instance = instance, **kwargs)
        # Hack the field ordering
        self.fields.keyOrder = ['plugin_name', 'container_type']
        
    def save(self, commit = True):
        pt = self.cleaned_data.pop('plugin_name')
        instance = self.instance
        if pt:
            instance.plugin_name = pt.name
        else:
            instance.plugin_name = ''
        return super(ContentBlockFormBase,self).save(commit = commit)


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
        

# Application view for handling change in content block internal plugin
# It handles two different Ajax interaction with the browser 
class ChangeContentView(appview.EditView):
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
        
    def plugin_form_id(self, instance):
        return '%s-options' % instance.pluginid()
    def plugin_preview_id(self, instance):
        return '%s-preview' % instance.pluginid()
            
    def get_form(self, djp, all = True):
        '''
        Get the contentblock editing form
        This form is composed of two formlet,
        one for choosing the plugin type,
        and one for setting the plugin options
        '''
        app      = self.appmodel
        instance = djp.instance
        fhtml    = form(method = app.form_method, url = djp.url)
        if app.form_ajax:
            fhtml.addClass(app.ajax.ajax)
        fhtml['topform'] = app.get_form(djp, wrapped = False)
        # We wrap the bottom part of the form with a div for ajax interaction
        div = htmlcomp('div', id = self.plugin_form_id(instance))
        fhtml['plugin']  = div
        if all:
            div['form'] = self.get_plugin_form(djp, instance.plugin)
            fhtml['submit'] = formlet(submit = submit(value = 'change'),
                                      layout = app.form_layout)
        return fhtml
        
    def get_plugin_form(self, djp, plugin):
        if plugin:
            instance = djp.instance
            args     = None
            if instance.plugin == plugin:
                args = instance.arguments
            pform = plugin.get_form(djp,args)
            if pform:
                return formlet(form = pform, layout = self.appmodel.form_layout)
    
    def edit_block(self, request):
        return jhtmls(identifier = '#%s' % self.instance.pluginid(),
                      html = self.instance.plugin_edit_block(request))
        
    def ajax__plugin_name(self, djp):
        '''
        Ajax post view function which handle the change of pluging within one html block.
        @param request: django HttpRequest instance
        @return JSON serializable object 
        '''
        form = self.get_form(djp, all = False)
        if form.is_valid():
            new_plugin = form.cleaned_data.get('plugin_name',None)
            pform      = self.get_plugin_form(djp, new_plugin)
            if pform:
                html = pform.render()
            else:
                html = u''
            return jhtmls(identifier = '#%s' % self.plugin_form_id(djp.instance),
                          html = html)
        else:
            return form.jerrors
        
    def ajax__container_type(self, djp):
        return self.ajax__plugin_name(djp)
    
    def default_ajax_view(self, djp):
        '''
        Ajax view called when changing the content plugin values.
        The instance.plugin object is maintained but its fields may change
        
        @param request: django HttpRequest instance
        @return JSON serializable object 
        '''
        form = self.get_form(djp, all = False)
        if form.is_valid():
            instance  = form.save(commit = False)
            pform     = instance.plugin.get_form(djp)
            instance.arguments = form2json(pform)
            instance.save()
            # We now serialize the argument form
            return jhtmls(identifier = '#%s' % self.plugin_preview_id(instance),
                          html = instance.render(djp)) 
        else:
            return form.jerrors
        
    def has_permission(self, request):
        if request.user.is_authenticated():
            return True
        else:
            return False
        

class DeleteContentView(appview.DeleteView):
    
    def __init__(self, **kwargs):
        super(DeleteContentView,self).__init__(**kwargs)
    
    def default_ajax_view(self, djp):
        request = djp.request
        if self.model.objects.delete_and_sort(djp.instance):
            pass
        else:
            pass


class ContentSite(appsite.ModelApplication):
    baseurl     = '%spage/' % basecontent
    pagemodel   = Page
    form        = ContentBlockForm
    form_layout = 'onecolumn'
    
    edit        = ChangeContentView()
    delete      = DeleteContentView(parent = 'edit')
    
    def submit(self, instance):
        return None
    
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
    inherit   = True
    
    
    
if appsite.site.editavailable:
    appsite.site.register(BlockContent,ContentSite,False)
    appsite.site.register(AppBlockContent,AppContentSite,False)
    
