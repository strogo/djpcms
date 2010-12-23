'''
Application for handling inline editing of blocks
The application derives from the base appsite.ModelApplication
and defines several subviews 
'''
from djpcms.conf import settings
from djpcms import forms, http
from djpcms.utils.translation import ugettext_lazy as _
from djpcms.core.exceptions import PermissionDenied
from djpcms.models import BlockContent
from django.template import RequestContext, loader, mark_safe
from djpcms.utils.func import isforminstance
from djpcms.utils.ajax import jhtmls, jremove, dialog, jempty, jerror
from djpcms.utils.html import submit, htmlcomp
from djpcms.utils.uniforms import UniForm, FormLayout
from djpcms.forms.cms import ContentBlockForm
from djpcms.plugins import get_plugin
from djpcms.plugins.extrawrappers import CollapsedWrapper
from djpcms.views import appsite, appview, handlers
from djpcms.views.cache import pagecache

dummy_wrap = lambda d,b,x : x


# Generator of content block in editing mode.
# Only called when we are in editing mode
class content_view(object):
    '''
    Utility class for creating the editing generator
    '''            
    def __init__(self, page, b):
        self.blockcontents = BlockContent.objects.for_page_block(page, b)
    
    def __call__(self, djp):
        '''Return a generator of edit blocks.
        '''
        request  = djp.request
        url      = djp.view.page_url(request)
        appmodel = appsite.site.for_model(BlockContent)
        editview = appmodel.getview('edit')
        wrapper  = EditWrapperHandler(url)
        pos = 0
        for b in self.blockcontents:
            if b.position != pos:
                b.position = pos
                b.save()
            pos += 1
            editdjp = editview(request, instance = b)
            djp.media += editdjp.media
            editdjp.media = djp.media
            html = editview.render(editdjp, url = url)
            yield wrapper.wrap(editdjp,b,html)


# Content wrapper in editing mode.
# Only called by content_view (function above)
class EditWrapperHandler(CollapsedWrapper):
    '''Wrapper for editing content
    '''
    auto_register = False
    def __init__(self, url):
        self.url = url
        
    def prefix(self, instance):
        '''prefix for given block'''
        return 'bd_%s' % instance.pluginid()
    
    def _wrap(self, djp, cblock, html):
        return ['edit-block'],djp.view.appmodel.deleteurl(djp.request, djp.instance)
    
    def footer(self, djp, cblock, html):
        return djp.view.get_preview(djp.request, djp.instance, self.url)


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
                                               isapp = False)
        
    def plugin_form_id(self, instance):
        return '%s-options' % instance.pluginid()
    def plugin_preview_id(self, instance):
        return '%s-preview' % instance.pluginid()
    def plugin_edit_id(self, instance):
        return '%s-edid' % instance.pluginid()
    
    def render(self, djp, url = None):
        return self.get_form(djp, url = url).render(djp)
    
    def get_preview(self, request, instance, url, wrapped = True, plugin = None):
        try:
            djpview = handlers.response(request, url[1:])
            preview_html = instance.render(djpview, plugin = plugin, wrapper = dummy_wrap)
        except Exception, e:
            preview_html = u'%s' % e
        if wrapped:
            return mark_safe('<div id="%s">%s</div>' % (self.plugin_preview_id(instance),preview_html))
        else:
            return preview_html
    
    def get_form(self, djp, all = True, url = None, **kwargs):
        '''Get the contentblock editing form
        This form is composed of two parts,
        one for choosing the plugin type,
        and one for setting the plugin options
        '''
        if url:
            initial = {'url':url}
        else:
            initial = None
        uni = super(ChangeContentView,self).get_form(djp, initial = initial)
        if all:
            instance = djp.instance
            pform,purl = self.get_plugin_form(djp, instance.plugin)
            id = self.plugin_form_id(instance)
            if pform:
                layout = getattr(pform,'layout',None) or FormLayout()
                layout.id = id
                pform.layout = layout
                uni.add(pform)
            else:
                # No plugin
                uni.add('<div id="%s"></div>' % id)
            sub = str(submit(value = "edit", name = 'edit_content'))
            id = self.plugin_edit_id(instance)
            cl = '' if purl else ' class="djphide"'
            uni.inputs.append(mark_safe('<span id="%s"%s>%s</span>' % (id,cl,sub)))
        return uni
        
    def get_plugin_form(self, djp, plugin, withdata = True):
        '''If *plugin* is not ``None``, it returns a tuple with the plugin form and the url for editing plugin contents.'''
        if plugin:
            instance = djp.instance
            args     = None
            if instance.plugin == plugin:
                args = instance.arguments
            pform = plugin.get_form(djp,args,withdata=withdata)
            purl  = djp.view.appmodel.pluginurl(djp.request, instance)
            return (pform,purl)
        else:
            return (None,None)
            
    def edit_block(self, request):
        return jhtmls(identifier = '#%s' % self.instance.pluginid(),
                      html = self.instance.plugin_edit_block(request))
        
    def ajax__plugin_name(self, djp):
        '''
        Ajax post view function which handle the change of pluging within one html block.
        It return JSON serializable object 
        '''
        form = self.get_form(djp, all = False)
        if form.is_valid():
            url        = form.cleaned_data['url']
            instance   = djp.instance
            new_plugin = form.cleaned_data.get('plugin_name',None)
            pform,purl = self.get_plugin_form(djp, new_plugin, withdata = False)
            if pform:
                html = UniForm(pform,tag=False).render(djp)
            else:
                html = u''
            data = jhtmls(identifier = '#%s' % self.plugin_form_id(djp.instance), html = html)
            preview = self.get_preview(djp.request, instance, url, plugin = new_plugin, wrapped = False)
            data.add('#%s' % self.plugin_preview_id(djp.instance), preview)
            id = self.plugin_edit_id(instance)
            if callable(new_plugin.edit_form):
                data.add('#%s' % id, type = 'show')
            else:
                data.add('#%s' % id, type = 'hide')
            return data
        else:
            return form.json_errors()
        
    def ajax__edit_content(self, djp):
        pluginview = self.appmodel.getview('plugin')
        return pluginview.default_post(pluginview(djp.request, instance = djp.instance))
        
    def ajax__container_type(self, djp):
        return self.ajax__plugin_name(djp)
    
    def default_post(self, djp):
        '''
        View called when changing the content plugin values.
        The instance.plugin object is maintained but its fields may change
        Only ajax post working for now.
        
        @param request: django HttpRequest instance
        @return JSON serializable object 
        '''
        # First get the plugin name
        is_ajax = djp.request.is_ajax()
        form = self.get_form(djp, all = False)
        instance = djp.instance
        request  = djp.request
        if form.is_valid():
            plugin = form.cleaned_data.get('plugin_name',None)
            instance.plugin_name = plugin.name
        else:
            if is_ajax:
                return form.json_errors()
            else:
                return djp.view.handle_response(djp)
        
        url   = form.cleaned_data['url']
        form  =  self.get_form(djp)
        if form.is_valid():
            forms      = list(form.forms_only())
            instance   = form[0].save(commit = False)
            pform = None if len(forms) == 1 else forms[1]
            #pform      = instance.plugin.get_form(djp)
            instance.arguments = instance.plugin.save(pform)
            instance.save()
            # We now serialize the argument form
            if is_ajax:
                preview = self.get_preview(request, instance, url,  wrapped = False)
                ret = jhtmls(identifier = '#%s' % self.plugin_preview_id(instance), html = preview)
                form.add_message(request, "Plugin changed to %s" % instance.plugin.description)
                ret.update(form.json_message())
                return ret
            else:
                pass 
        else:
            if is_ajax:
                return form.json_errors()
            else:
                pass
            
    def get_preview_response(self, djp, url):
        instance = djp.instance
        preview = self.get_preview(djp.request, instance, url,  wrapped = False)
        return jhtmls(identifier = '#%s' % self.plugin_preview_id(instance), html = preview)
        

class EditPluginView(appview.EditView):
    '''View class for editing the content of a plugin. Not all plugins have an editing view.
The url is given by the ContentBlocks models
    '''
    _methods = ('post',)
    
    def __init__(self, regex = 'plugin', parent = 'edit'):
        super(EditPluginView,self).__init__(regex = regex,
                                            parent = parent,
                                            isapp = False)
    
    def get_form(self, djp, withdata = True, initial = None, **kwargs):
        instance = djp.instance
        p = instance.plugin
        if p:
            return p.edit(djp, instance.arguments, initial = initial, withdata = withdata)
                
    
    def default_post(self, djp):
        data = dict(djp.request.POST.items())
        is_ajax = djp.request.is_ajax()
        try:
            f = self.get_form(djp, initial = {'url':data['url']}, withdata = False)
        except PermissionDenied, e:
            return jerror(str(e))
        
        if f:
            uni = UniForm(f,
                          request  = djp.request,
                          action = djp.url).addClass(djp.css.ajax).addClass('editing')
            if is_ajax:
                d = dialog(hd = unicode(f.instance),
                           bd = uni.render(djp),
                           modal  = True,
                           width  = settings.CONTENT_INLINE_EDITING.get('width','auto'),
                           height = settings.CONTENT_INLINE_EDITING.get('height','auto'))
                d.addbutton('Ok', url = djp.url, func = 'save')
                d.addbutton('Cancel', func = 'cancel')
                d.addbutton('Save', url = djp.url, func = 'save', close = False)
                return d
            else:
                #todo write the non-ajax POST view
                pass
        else:
            return jerror('Nothing selected. Cannot edit.')
    
    def ajax__save(self, djp):
        f = self.get_form(djp)
        if f.is_valid():
            f.save()
            instance = djp.instance
            editview = self.appmodel.getview('edit')
            return editview.get_preview_response(djp,f.cleaned_data['url'])
        else:
            return f.json_errors()
        


class ContentSite(appsite.ModelApplication):
    '''AJAX enabled applications for changing content of a page.'''
    form        = ContentBlockForm
    form_layout = 'onecolumn'
    hidden      = True
    
    edit        = ChangeContentView()
    delete      = appview.DeleteView(parent = 'edit')
    plugin      = EditPluginView(regex = 'plugin', parent = 'edit')
    
    class Media:
        js = ['djpcms/iNettuts.js']
    
    def submit(self, *args, **kwargs):
        return [submit(value = "save", name = '_save')]
    
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
        view = self.getview('plugin')
        if view and self.has_edit_permission(request, obj):
            djp = view(request, instance = obj)
            return djp.url
        
    def get_object(self, request, pageid = 1, blocknumber = 1, position = 1):
        '''
        Override superclass function.
        This function get the information needed for performing in-line editing.
        @param request: django HttpRequest instance
        @param pageid:  a page id (a string to be converted into an integer)
        @param blocknumber:  block number within the page (a string to be converted into an integer)
        @param position:  position number within the block (a string to be converted into an integer)
        @return None
        '''
        pageid       = int(pageid)
        blocknumber  = int(blocknumber)
        position     = int(position)
        page         = pagecache.get_from_id(pageid)
        blocks       = self.model.objects.filter(page = page)
        inner        = page.inner_template
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
    