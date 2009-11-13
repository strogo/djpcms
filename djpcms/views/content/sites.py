import copy

from django.http import Http404, HttpResponse, HttpResponseRedirect

from djpcms.settings import HTML_CLASSES
from djpcms.models import BlockContent, AppBlockContent, Page, AppPage
from djpcms.views.baseview import djpcmsview
from djpcms.views.contentgenerator import ContentBlockForm, AppContentBlockForm
from djpcms.utils.ajax import jhtmls
    
    
    
class ContentSite(djpcmsview):
    '''
    View class for managing inline editing of a content block.
    The url is given by the ContentBlocks models
    '''    
    def methods(self, request):
        return ('post',)
    
    def get_urls(self):
        '''
        Set up urls
        '''
        from django.conf.urls.defaults import patterns, url
        #url(r'^(\d+)/(\d+)/(\d+)/(?P<plugin>\d+)/$', self.response, name = 'edit_content_block'),
        urlpatterns = patterns('',
            url(r'^(\d+)/(\d+)/(\d+)/(\d+)/$', self.response, name = 'edit_content_block'),
            )
        
        return urlpatterns
    
    def urls(self):
        return self.get_urls()
    urls = property(urls)
    
    def handle_reponse_arguments(self, request, pagetype, pageid, blocknumber, position):
        '''
        Override superclass function.
        This function get the information needed for performing in-line editing.
        @param request: django HttpRequest instance
        @param pageid:  a page id (a string to be converted into an integer)
        @param blocknumber:  block number within the page (a string to be converted into an integer)
        @param position:  position number within the block (a string to be converted into an integer)
        @return None
        '''
        try:
            pagetype    = int(pagetype)
            pageid      = int(pageid)
            blocknumber = int(blocknumber)
            position    = int(position)
            view        = copy.copy(self)
            #TODO
            #Clean up this
            if pagetype == 0:
                view.pagemodel  = Page
                view.blockmodel = BlockContent
                view.blockform  = ContentBlockForm
            else:
                view.pagemodel  = AppPage
                view.blockmodel = AppBlockContent
                view.blockform  = AppContentBlockForm
            page   = view.pagemodel.objects.get(pk = pageid)
        except:
            raise Http404('Page not available')
        
        blocks = view.blockmodel.objects.filter(page = pageid)
        nblocks = page.numblocks()
        if blocknumber >= nblocks:
            raise Http404('Block number too high for current page')
    
        blocks = view.blockmodel.objects.filter(page = page)
        cb     = blocks.count()
    
        # Create new blocks if necessary
        for bn in range(cb,nblocks):
            b = view.blockmodel(page = page, block = bn)
            b.save()
    
        try:
            view.instance = view.blockmodel.objects.get(page = page, block = blocknumber, position = position)
        except:
            raise Http404('Position %s not available in content block %s' % (position,blocknumber))
            
        view.url = view.instance.url()
        return view
       
    def edit_block(self, request):
        return jhtmls(identifier = '#%s' % self.instance.pluginid(),
                      html = self.instance.plugin_edit_block(request))
        
    def ajax__plugin_name(self, request):
        '''
        Ajax post view function which handle the change of pluging within
        one html block.
        @param request: django HttpRequest instance
        @return JSON serializable object 
        '''        
        form = self.blockform(instance = self.instance, data = request.POST)
        if form.is_valid():
            self.instance = form.save()
            cl = self.requestview(request)
            return jhtmls(identifier = '#%s' % self.instance.pluginid(),
                          html = self.instance.plugin_edit_block(cl))
        else:
            pass
        
    def ajax__container_type(self, request):
        return self.ajax__plugin_name(request)            
        
    def ajax__delete_plugin(self, request):
        '''
        Here we delete the BlockContent.
        Deletion only happens when the blockcontent instance has
        a plugin.
        '''
        if BlockContent.objects.delete_and_sort(self.instance):
            pass
        else:
            pass
    
    def ajax__change_plugin_content(self, request):
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
    
    
    def default_ajax_view(self, request):
        '''
        Ajax view called when changing the plugin values
        '''
        return self.instance.change_plugin(request, self.ajax_key)
        
        
        
    def has_permission(self, request):
        if request.user.is_authenticated():
            return True
        else:
            return False
        
    
site = ContentSite()