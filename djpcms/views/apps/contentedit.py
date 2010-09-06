'''
Application for handling inline editing of blocks
The application derives from the base appsite.ModelApplication
and defines several subviews 
'''
from django import http
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext, loader

from djpcms.conf import settings
from djpcms.models import BlockContent
from djpcms.utils import form_kwargs, mark_safe
from djpcms.utils.func import isforminstance
from djpcms.utils.ajax import jhtmls, jremove, dialog, jempty
from djpcms.utils.html import form, formlet, submit, htmlcomp
from djpcms.utils.uniforms import UniForm, FormLayout
from djpcms.forms import ContentBlockForm
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
        '''
        Return a generator
        blockcontents is a queryset of BlockContent model
        '''
        request  = djp.request
        url      = '/'.join(request.path.split('/')[2:])
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
        '''
        prefix for given block
        '''
        return 'bd_%s' % instance.pluginid()
    
    def _wrap(self, djp, cblock, html):
        c = super(EditWrapperHandler,self)._wrap(djp, cblock, html)
        view     = djp.view
        instance = djp.instance
        menulist = c['menulist']
        c['classes'].append('edit-block')
        delurl   = view.appmodel.deleteurl(djp.request, instance)
        if delurl:
            menulist.append(mark_safe('<a class="deletable" href="%s">DELETE</a>' % delurl))
        return c
    
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
                                               isapp = False,
                                               name = 'edit_content_block')
        
    def plugin_form_id(self, instance):
        return '%s-options' % instance.pluginid()
    def plugin_preview_id(self, instance):
        return '%s-preview' % instance.pluginid()
    def plugin_edit_id(self, instance):
        return '%s-edid' % instance.pluginid()
    
    def render(self, djp, url = None):
        uni = self.get_form(djp, url = url)
        djp.media += uni.media
        return uni.render()
    
    def get_preview(self, request, instance, url, wrapped = True, plugin = None):
        try:
            djpview = handlers.response(request, url)
            preview_html = instance.render(djpview, plugin = plugin, wrapper = dummy_wrap)
        except Exception, e:
            preview_html = u'%s' % e
        if wrapped:
            return mark_safe('<div id="%s">%s</div>' % (self.plugin_preview_id(instance),preview_html))
        else:
            return preview_html
    
    def get_form(self, djp, all = True, url = None, **kwargs):
        '''Get the contentblock editing form
        This form is composed of two formlet,
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
                uni.add('<div id="%s"></div' % id)
            if purl:
                sub = str(submit(value = "edit", name = 'edit_content'))
            else:
                sub = ''
            id = self.plugin_edit_id(instance)
            uni.inputs.append(mark_safe('<span id="%s">%s</span>' % (id,sub)))
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
        @param request: django HttpRequest instance
        @return JSON serializable object 
        '''
        form = self.get_form(djp, all = False)
        if form.is_valid():
            url        = form.cleaned_data['url']
            instance   = djp.instance
            new_plugin = form.cleaned_data.get('plugin_name',None)
            pform,purl = self.get_plugin_form(djp, new_plugin, withdata = False)
            if pform:
                html = UniForm(pform,tag=False).render()
            else:
                html = u''
            data = jhtmls(identifier = '#%s' % self.plugin_form_id(djp.instance), html = html)
            preview = self.get_preview(djp.request, instance, url, plugin = new_plugin, wrapped = False)
            data.add('#%s' % self.plugin_preview_id(djp.instance), preview)
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
                pass
        
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
    
    def get_form(self, djp, withdata = True, **kwargs):
        instance = djp.instance
        p = instance.plugin
        if p:
            flet = p.edit(djp, instance.arguments, withdata = withdata)
            if isforminstance(flet):
                flet = formlet(form = flet,
                               layout = 'onecolumn')
            if isinstance(flet,formlet):
                f = form(url = djp.url, cn = self.ajax.ajax)
                f['form'] = flet
                return f
    
    def default_post(self, djp):
        is_ajax = djp.request.is_ajax()
        f = self.get_form(djp, withdata = False)
        if is_ajax:
            d = dialog(hd = f.instance.code,
                       bd = f.render(),
                       modal  = True,
                       width  = settings.CONTENT_INLINE_EDITING.get('width','auto'),
                       height = settings.CONTENT_INLINE_EDITING.get('height','auto'))
            d.addbutton('Ok', url = djp.url, func = 'save')
            d.addbutton('Cancel', url = djp.url, func = 'cancel')
            d.addbutton('Save', url = djp.url, func = 'save', close = False)
            return d
        else:
            #todo write the non-ajax POST view
            pass
    
    def ajax__save(self, djp):
        f = self.get_form(djp)
        if f.is_valid():
            f.save()
            return f.messagepost('%s saved' % f.instance)
        else:
            return f.json_errors()
        
    def ajax__cancel(self, djp):
        return jempty()


class ContentSite(appsite.ModelApplication):
    form        = ContentBlockForm
    form_layout = 'onecolumn'
    
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
    
    
if appsite.site.editavailable:
    baseurl     = settings.CONTENT_INLINE_EDITING.get('pagecontent', '/content/')
    appsite.site.register(baseurl,
                          ContentSite,
                          model = BlockContent,
                          editavailable = False)
    
