from django import http
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext, loader

from djpcms.settings import HTML_CLASSES, CONTENT_INLINE_EDITING
from djpcms.models import BlockContent, Page
from djpcms.utils import form_kwargs
from djpcms.utils.func import isforminstance
from djpcms.utils.ajax import jhtmls, jremove, dialog, jempty
from djpcms.utils.html import form, formlet, submit, htmlcomp
from djpcms.forms import ContentBlockForm
from djpcms.plugins import get_plugin, ContentWrapper
from djpcms.views import appsite, appview


# Generator of content block in editing mode.
# Only called when we are in editing mode
class content_view(object):
    '''
    Utility class for creating the editing generator
    '''
    def __init__(self, page):
        pass
            
    def blockcontents(self, page, b):
        return BlockContent.objects.for_page_block(page, b)
    
    def __call__(self, request, blockcontents):
        '''
        Return a generator
        '''
        appmodel = appsite.site.for_model(BlockContent)
        view = appmodel.getapp('edit')
        wrapper = EditWrapperHandler()
        for b in blockcontents:
            djp  = view.requestview(request, instance = b)
            djp.wrapper = wrapper
            #djp.prefix  = wrapper.prefix(b)
            yield wrapper.wrap(djp)


# Content wrapper in editing mode.
# Only called by content_view (funation above)
class EditWrapperHandler(ContentWrapper):
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
        plgurl   = view.appmodel.pluginurl(djp.request, instance)
        plugin = False
        if instance.plugin:
            plugin = True
        c = {'djp':               djp,
             'form':              form,
             'preview':           html,
             'instance':          instance,
             'plugin':            plugin,
             'deleteurl':         delurl,
             'pluginurl':         plgurl,
             'plugin_preview_id': view.plugin_preview_id(instance)}
        return loader.render_to_string(["content/edit_block.html",
                                        "djpcms/content/edit_block.html"],
                                        c)


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
                                               isapp = False,
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
        form = self.get_form(djp, all = True)
        if form.is_valid():
            instance  = form.save(commit = False)
            pform     = instance.plugin.get_form(djp)
            instance.arguments = instance.plugin.save(pform)
            instance.save()
            # We now serialize the argument form
            ret = jhtmls(identifier = '#%s' % self.plugin_preview_id(instance),
                         html = instance.render(djp))
            ret.update(form.messagepost("Plugin changed to %s" % instance.plugin.description))
            return ret 
        else:
            return form.jerrors
        

class EditPluginView(appview.EditView):
    '''
    View class for managing inline editing of a content block.
    The url is given by the ContentBlocks models
    '''
    _methods = ('post',)
    
    def __init__(self, regex = 'plugin', parent = 'edit'):
        super(EditPluginView,self).__init__(regex = regex,
                                            parent = parent,
                                            isapp = False,
                                            name = 'edit_plugin')
    
    def get_form(self, djp, withdata = True):
        instance = djp.instance
        p = instance.plugin
        if p:
            f = p.edit(djp, instance.arguments, withdata = withdata)
            if f:
                if isforminstance(f):
                    flet = formlet(form = f,
                                   layout = 'onecolumn')
                    f = form(url = djp.url, cn = self.ajax.ajax)
                    f['form'] = flet
                return f
    
    def default_ajax_view(self, djp):
        f = self.get_form(djp, withdata = False)
        d = dialog(hd = f.instance.code,
                   bd = f.render(),
                   modal = True,
                   width = 600)
        d.addbutton('Ok', url = djp.url, func = 'save')
        d.addbutton('Cancel', url = djp.url, func = 'cancel')
        d.addbutton('Save', url = djp.url, func = 'save', close = False)
        return d
    
    def ajax__save(self, djp):
        f = self.get_form(djp)
        if f.is_valid():
            f.save()
            return f.messagepost('%s saved' % f.instance)
        else:
            return f.jerrors
        
    def ajax__cancel(self, djp):
        return jempty()


class ContentSite(appsite.ModelApplication):
    baseurl     = CONTENT_INLINE_EDITING.get('pagecontent', '/content/')
    pagemodel   = Page
    form        = ContentBlockForm
    form_layout = 'onecolumn'
    
    edit        = ChangeContentView()
    delete      = appview.DeleteView(parent = 'edit')
    plugin      = EditPluginView(regex = 'plugin', parent = 'edit')
    
    def submit(self, instance):
        return None
    
    def objectbits(self, obj):
        return {'pageid': obj.page.id,
                'blocknumber': obj.block,
                'position': obj.position}
    
    def remove_object(self, obj):
        bid = obj.htmlid()
        if self.model.objects.delete_and_sort(obj):
            return bid
        
    def pluginurl(self, request, obj):
        p = obj.plugin
        if not p or not p.edit_form:
            return
        view = self.getapp('plugin')
        if view and self.has_edit_permission(request, obj):
            djp = view.requestview(request, instance = obj)
            return djp.url
        
        
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
        inner       = page.inner_template
        if inner:
            nblocks     = inner.numblocks()
        else:
            nblocks     = 0
            
        if blocknumber >= nblocks:
            # TODO Remove blocks
            raise ValueError('Block number too high for current page')
        
        if nblocks:
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
        else:
            return None
    
    
if appsite.site.editavailable:
    appsite.site.register(BlockContent,ContentSite,False)
    
