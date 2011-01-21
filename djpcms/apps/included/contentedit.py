'''
Application for handling inline editing of blocks
The application derives from the base appsite.ModelApplication
and defines several ajax enabled sub-views 
'''
from djpcms import forms, sites
from djpcms.core.page import block_htmlid
from djpcms.utils.translation import ugettext_lazy as _
from djpcms.core.exceptions import PermissionDenied
from djpcms.models import BlockContent
from djpcms.template import RequestContext, loader, mark_safe
from djpcms.utils.func import isforminstance
from djpcms.utils.ajax import jhtmls, jremove, dialog, jempty, jerror, jattribute, jcollection
from djpcms.utils.html import input, htmlcomp
#from djpcms.utils.uniforms import UniForm, FormLayout
from djpcms.forms.cms import ContentBlockForm
from djpcms.plugins import get_plugin
from djpcms.plugins.extrawrappers import CollapsedWrapper
from djpcms.views import appsite, appview, view_edited_url

dummy_wrap = lambda d,b,x : x


# Content wrapper in editing mode.
# Only called by content_view (function above)
class EditWrapperHandler(CollapsedWrapper):
    '''Wrapper for editing content
    '''
    auto_register = False
    def __init__(self, url):
        self.url = url
        
    def __call__(self, djp, cblock, html):
        return self.wrap(djp, cblock, html)
    
    def id(self, cblock):
        return cblock.htmlid()
    
    def _wrap(self, djp, cblock, html):
        cl = ['edit-block']
        if cblock.plugin_name:
            cl.append('movable')
        return cl,djp.view.appmodel.deleteurl(djp.request, djp.instance)
    
    def footer(self, djp, cblock, html):
        return djp.view.get_preview(djp.request, djp.instance, self.url)


def update_contentblock(djp, cblock, block, position, jattr):
        '''Update a contentblock by changing its ``block`` and ``position`` values.'''
        view = djp.view
        if cblock.block == block and cblock.position == position:
            return 
        id = 'id'
        oldid = cblock.htmlid()
        plgid1 = cblock.pluginid('options')
        plgid2 = cblock.pluginid('preview')
        plgid3 = cblock.pluginid('edit')
        cblock.block = block
        cblock.position = position
        cblock.save()
        cdjp = view(djp.request, instance = cblock)
        jattr.add('div#{0} form.djpcms-blockcontent'.format(oldid),'action',cdjp.url)
        durl = view.appmodel.deleteurl(djp.request, cblock)
        jattr.add('div#{0} div.hd a.deletable'.format(oldid),'href',durl)
        jattr.add('#'+oldid, id,cblock.htmlid())
        jattr.add('#'+plgid1,id,cblock.pluginid('options'))
        jattr.add('#'+plgid2,id,cblock.pluginid('preview'))
        jattr.add('#'+plgid3,id,cblock.pluginid('edit'))
        
        
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
        
    def render(self, djp, url = None):
        return self.get_form(djp, url = url).render(djp)
    
    def get_preview(self, request, instance, url, wrapped = True, plugin = None):
        try:
            djpview = sites.djp(request, url[1:])
            preview_html = instance.render(djpview, plugin = plugin, wrapper = dummy_wrap)
        except Exception, e:
            preview_html = u'%s' % e
        if wrapped:
            return mark_safe('<div id="%s">%s</div>' % (instance.pluginid('preview'),preview_html))
        else:
            return preview_html
    
    def get_form(self, djp, all = True, url = None, initial = None, **kwargs):
        '''Get the contentblock editing form
        This form is composed of two parts,
        one for choosing the plugin type,
        and one for setting the plugin options
        '''
        if url:
            initial = initial if initial is not None else {}
            initial['url'] = url
        else:
            initial = None
        uni = super(ChangeContentView,self).get_form(djp,
                                                     initial = initial,
                                                     **kwargs)
        if all:
            instance = djp.instance
            pform,purl = self.get_plugin_form(djp, instance.plugin)
            id = instance.pluginid('options')
            if pform:
                layout = getattr(pform,'layout',None) or FormLayout()
                layout.id = id
                pform.layout = layout
                uni.add(pform)
            else:
                # No plugin
                uni.add('<div id="%s"></div>' % id)
            sub = input(value = "edit", name = 'edit_content').render()
            id = instance.pluginid('edit')
            cl = '' if purl else ' class="djphide"'
            uni.inputs.append('<span id="{0}"{1}>{2}</span>'.format(id,cl,sub))
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
        return jhtmls(identifier = '#' + self.instance.pluginid(),
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
            data = jhtmls(identifier = '#%s' % instance.pluginid('options'), html = html)
            preview = self.get_preview(djp.request, instance, url, plugin = new_plugin, wrapped = False)
            data.add('#%s' % instance.pluginid('preview'), preview)
            id = instance.pluginid('edit')
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
    
    def _blockpos(self, id):
        pageid, block, pos = (id.split('-')[-3:])
        return int(block),int(pos)
        
    def ajax__rearrange(self, djp):
        '''Move the content block to a new position and updates all html attributes'''
        contentblock = djp.instance
        page   = contentblock.page
        oldposition = contentblock.position
        oldblock = contentblock.block
        data   = dict(djp.request.POST.items())
        try:            
            previous = data.get('previous',None)
            if previous:
                block, pos = self._blockpos(previous)
                newposition = pos + 1
            else:
                nextv = data.get('next',None)
                if nextv:
                    block, pos = self._blockpos(nextv)
                else:
                    return jempty()
                newposition = pos if not pos else pos-1
            
            if block == contentblock.block and contentblock.position == newposition:
                # Nothing to do
                return jempty()
            else:
                filter = self.model.objects.filter
                jattr = jattribute()
                
                if block == oldblock:
                    # On the same block
                    contentblock.position = 1000
                    contentblock.save()
                    mblocks = filter(page = page, block = block)
                    step = -1
                    if newposition > oldposition:
                        newposition -= 1
                        step = 1
                    for position in range(oldposition,newposition,step):
                        iblock = mblocks.get(position = position+step)
                        update_contentblock(djp,iblock,block,position,jattr)
                    contentblock.position = oldposition
                    update_contentblock(djp,contentblock,block,newposition,jattr)                    
                else:
                    # On a different block
                    cmp = lambda x,y : 1 if y.position > x.position else -1
                    # First move to the new block
                    for cblock in sorted(filter(page = page, block = block),cmp):
                        if cblock.position >= newposition:
                            update_contentblock(djp,cblock,block,cblock.position+1,jattr)
                    update_contentblock(djp,contentblock,block,newposition,jattr)
                    # Second rearrange old block
                    for cblock in filter(page = page, block = oldblock):
                        if cblock.position > oldposition:
                            update_contentblock(djp,cblock,oldblock,cblock.position-1,jattr)                
                return jattr
        except Exception as e:
            return jerror('Could not find target block. {0}'.format(e))
        
    
    def default_post(self, djp):
        '''View called when changing the content plugin values.
The instance.plugin object is maintained but its fields may change.'''
        # First get the plugin name
        is_ajax = djp.request.is_ajax()
        form = self.get_form(djp, all = False)
        
        if not form.is_valid():
            if is_ajax:
                return form.json_errors()
            else:
                return djp.view.handle_response(djp)
        
        instance = djp.instance
        request = djp.request
        cd = form.cleaned_data
        plugin = cd['plugin_name']
        url = cd['url']
        instance.plugin_name = plugin.name
        
        # Get the full form
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
                page = instance.page
                block = instance.block
                preview = self.get_preview(request, instance, url,  wrapped = False)
                jquery = jhtmls(identifier = '#%s' % instance.pluginid('preview'), html = preview)
                form.add_message(request, "Plugin changed to %s" % instance.plugin.description)
                jquery.update(form.json_message())
                cblocks = self.model.objects.filter(page = page, block = block)
                if instance.position == cblocks.count()-1:
                    b = page.get_block(block)
                    editdjp = self(request, instance = b)
                    html = self.render(editdjp, url = url)
                    wrapper  = EditWrapperHandler(url)
                    html = wrapper(editdjp,b,html)
                    jquery.add('#'+block_htmlid(page.id,block),html,'append')
                return jquery
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
        return jhtmls(identifier = '#%s' % instance.pluginid('preview'), html = preview)
        
        
class DeleteContentView(appview.DeleteView):
    
    def default_post(self, djp):
        instance = djp.instance
        block  = instance.block
        jquery = jcollection()
        blockcontents = self.model.objects.for_page_block(instance.page, block)
        if instance.position == blockcontents.count() - 1:
            return jquery
        
        jatt   = jattribute()
        pos    = 0
        for b in blockcontents:
            if b == instance:
                jquery.append(jremove('#'+instance.htmlid()))
                b.delete()
                continue
            if b.position != pos:
                update_contentblock(djp, b, block, pos, jatt)
            pos += 1
        jquery.append(jatt)

        if djp.request.is_ajax():
            return jquery
        else:
            refer = sjp.request.environ.get('HTTP_REFERER')
            return self.redirect(refer)
    

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
        prefix = data['_prefixed']
        is_ajax = djp.request.is_ajax()
        try:
            initial = {'url':data['{0}-url'.format(prefix)]}
            f = self.get_form(djp, initial = initial, withdata = False)
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
                           width  = djp.settings.CONTENT_INLINE_EDITING.get('width','auto'),
                           height = djp.settings.CONTENT_INLINE_EDITING.get('height','auto'))
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
    delete      = DeleteContentView(parent = 'edit')
    plugin      = EditPluginView(regex = 'plugin', parent = 'edit')
    
    def submit(self, *args, **kwargs):
        return [input(value = "save", name = '_save')]
    
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
        page         = request.site.pagecache.get_from_id(pageid)
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
                raise request.http.Http404('Position %s not available in content block %s' % (position,blocknumber))
        
            return instance
        else:
            return None

    def blocks(self, djp, page, b):
        '''Return a generator of edit blocks.
        '''
        blockcontents = self.model.objects.for_page_block(page, b)
        request  = djp.request
        url      = djp.view.page_url(request)
        editview = self.getview('edit')
        wrapper  = EditWrapperHandler(url)
        pos = 0
        Tot = blockcontents.count() - 1
        for b in blockcontents:
            if not b.plugin_name and b.position < Tot:
                b.delete()
                continue  
            if b.position != pos:
                b.position = pos
                b.save()
            pos += 1
            editdjp = editview(request, instance = b)
            djp.media += editdjp.media
            editdjp.media = djp.media
            html = editview.render(editdjp, url = url)
            yield wrapper(editdjp,b,html)
