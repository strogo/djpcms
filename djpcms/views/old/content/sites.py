from django import http

from djpcms.settings import HTML_CLASSES, CONTENT_INLINE_EDITING
from djpcms.models import BlockContent, AppBlockContent, Page, AppPage
from djpcms.plugins.application import appsite
from djpcms.views.appview import ObjectView
from djpcms.views.contentgenerator import ContentBlockForm, AppContentBlockForm
from djpcms.utils import form_kwargs
from djpcms.utils.ajax import jhtmls
    

basecontent = CONTENT_INLINE_EDITING.get('pagecontent', '/content/')


class ContentSite(appsite.ModelApplication):
    baseurl   = '%spage/' % basecontent
    pagemodel = Page
    form      = ContentBlockForm
    
    main      = ChangeContentView()
    
    def objectbits(self, obj):
        return {'pageid': obj.page.id,
                'blocknumber': self.block,
                'position': self.position}
        
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
    
    
    
    
class ChangeContentView(ObjectView):
    '''
    View class for managing inline editing of a content block.
    The url is given by the ContentBlocks models
    '''
    methods = ('post',)
    
    def __init__(self):
        regex = '(?P<pageid>\d+)/(?P<blocknumber>\d+)/(?P<position>\d+)'
        super(ChangeContentView,self).__init__(regex = regex)
       
    def edit_block(self, request):
        return jhtmls(identifier = '#%s' % self.instance.pluginid(),
                      html = self.instance.plugin_edit_block(request))
        
    def ajax__plugin_name(self, djp):
        '''
        Ajax post view function which handle the change of pluging within one html block.
        @param request: django HttpRequest instance
        @return JSON serializable object 
        '''
        instance = self.get_block(djp)
        form = self.blockform(**form_kwargs(instance = self.instance, request = djp.request))
        if form.is_valid():
            self.instance = form.save()
            return jhtmls(identifier = '#%s' % self.instance.pluginid(),
                          html = self.instance.plugin_edit_block(djp))
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
        
    
    
if CONTENT_INLINE_EDITING.get('available',False):
    appsite.site.register(BlockContent,ContentSite,False)
    appsite.site.register(AppBlockContent,AppContentSite,False)


