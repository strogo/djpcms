import datetime
import re

try:
    from django.contrib import messages
except:
    messages = None
from django.http import Http404
from django.utils.dateformat import DateFormat
from django.db import models
from django.utils import translation
from django.utils import html
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.datastructures import SortedDict
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.template import Template

#from djcms.middleware.threadlocals import get_current_user
from djpcms.fields import SlugCode
from djpcms.plugins import get_wrapper, default_content_wrapper, get_plugin
from djpcms.utils.models import TimeStamp
from djpcms.utils import lazyattr, function_module, force_unicode, mark_safe, htmltype
from djpcms.utils.func import PathList
from djpcms.uploads import upload_function, site_image_storage
from djpcms.managers import PageManager
from djpcms.markup import markuplib

protocol_re = re.compile('^\w+://')
    

class InnerTemplate(TimeStamp):
    '''
    Page Inner template
    '''
    name     = models.CharField(max_length = 200)
    image    = models.ImageField(upload_to = upload_function, storage = site_image_storage(), null = True, blank = True)
    template = models.TextField(blank = True)
    blocks   = models.TextField(help_text = _('comma separated strings indicating the content blocks'))
        
    def __unicode__(self):
        return u'%s' % self.name
    
    def render(self, c):
        '''
        Render the inner template given the content
        @param param: c content dictionary or instance of Context
        @return: html 
        '''
        return Template(self.template).render(c)
        
    def numblocks(self):
        bs = self.blocks.split(',')
        return len(bs)
    
    
class CssPageInfo(TimeStamp):
    '''
    Css information for the Page
    '''
    body_class_name      = models.CharField(max_length = 60, blank = True)
    container_class_name = models.CharField(max_length = 60, blank = True)
    fixed    = models.BooleanField(default = True)
    gridsize = models.PositiveIntegerField(default = 12)
        
    def __unicode__(self):
        if self.body_class_name:
            return u'%s - %s' % (self.body_class_name,self.conteiner_class())
        else:
            return self.conteiner_class()
        
    def conteiner_class(self):
        '''
        Get the container class-name.
        If not specified it return container_gridsize for 960 grid templates
        '''
        if not self.container_class_name:
            return u'container_%s' % self.gridsize
        else:
            return self.container_class_name
    
    
class Page(TimeStamp):
    site        = models.ForeignKey(Site)
    application = models.CharField(max_length = 200, blank = True)
    redirect_to = models.ForeignKey('self',
                                    null  = True,
                                    blank = True,
                                    related_name = 'redirected_from')
    title       = models.CharField(max_length = 60,
                                   blank = True,
                                   help_text=_('Optional. Page Title.'))
    
    url_pattern = models.CharField(max_length = 200,
                                   blank = True,
                                   help_text=_('URL bit for flat pages only'))
    
    link        = models.CharField(max_length = 60,
                                   blank = True,
                                   help_text=_('Short name to display as link to this page.'),
                                   verbose_name = 'link name')
    
    inner_template = models.ForeignKey(InnerTemplate,
                                       null = True,
                                       blank = True,
                                       verbose_name=_("inner template"))
    
    template    = models.CharField(max_length=200,
                                   verbose_name = 'template file',
                                   null = True,
                                   blank = True,
                                   help_text=_('Optional. Templale file for the page.'))
    
    in_navigation = models.PositiveIntegerField(default=1,
                                                help_text = _("Position in navigation. If 0 it won't be in navigation"))
    
    cssinfo     = models.ForeignKey(CssPageInfo,
                                    null = True,
                                    blank = True,
                                    verbose_name='Css classes')
    
    is_published = models.BooleanField(default=True,
                                       help_text=_('Whether or not the page is accessible from the web.'),
                                       verbose_name='published')
    # Access
    requires_login = models.BooleanField(verbose_name = 'login',
                                         help_text=_('If checked, only logged-in users can view the page.'))
       
    soft_root = models.BooleanField(_("soft root"),
                                    db_index=True,
                                    default=False,
                                    help_text=_("All ancestors will not be displayed in the navigation"))
    
    # Navigation
    parent    = models.ForeignKey('self',
                                  null  = True,
                                  blank = True,
                                  related_name = 'children',
                                  help_text=_('This page will be appended inside the chosen parent page.'))
    
    code_object = models.CharField(max_length=200,
                                   blank=True,
                                   verbose_name = 'in sitemap',
                                   help_text=_('Optional. Dotted path to a python class dealing with requests'))
    
    doctype = models.PositiveIntegerField(default = htmltype.htmldefault,
                                          choices = htmltype.htmldocs)
    insitemap = models.BooleanField(default = True,
                                    verbose_name = 'in sitemap',
                                    help_text=_('If the page is public, include it in sidemap or not.'))
        
    # Denormalized level in the tree and url, for performance 
    level       = models.IntegerField(default = 0, editable = False)
    url         = models.CharField(editable = False, max_length = 1000)

    objects = PageManager()

    class Meta:
        get_latest_by   = 'last_modified'
        verbose_name_plural = "Sitemap"

    def __unicode__(self):
        return u'%s%s' % (self.site.domain,self.url)
    
    def save(self, **kwargs):
        self.url   = self.__calculate_url()
        if self.url is None:
            return
        self.level = self.get_level()
        super(Page,self).save(**kwargs)
        
    def get_template(self):
        '''
        HTML template for the page
        if not specified we get the template of the parent page
        '''
        if not self.template:
            if self.parent:
                return self.parent.get_template()
            else:
                return 'base.html'
        else:
            return self.template

    @lazyattr
    def get_parent_path(self):
        path = []
        parent = self.parent
        while parent:
            path.append(parent)
            parent = parent.parent
        return PathList(reversed(path))
        
    @lazyattr
    def get_path(self):
        p = self.get_parent_path()
        p.append(self)
        return p

    def on_path(self, super):
        return super in self.get_path()
        
    def __calculate_url(self):
        '''
        Calculate the url.
        '''
        try:
            if self.application:
                from djpcms.views import appsite
                app = appsite.site.getapp(self.application)
                purl = app.urlbit.url
                if app.isroot():
                    baseurl = app.baseurl
                    root    = Page.objects.filter(site = self.site, level = 0)
                    if baseurl == '/':
                        if root:
                            if messages:
                                messages.error("Root page already available, cannot set application as root. Delete the flat root page first")
                            return
                        self.parent = None
                    else:
                        urls = baseurl[1:-1].split('/')
                        if len(urls) > 1:
                            parent_url = '/%s/' % '/'.join(urls[:-1])
                            root    = Page.objects.filter(site = self.site, url = parent_url)
                        else:
                            parent_url = '/'
                            
                        if root:
                            self.parent = root[0]
                        else:
                            if messages:
                                messages.error('Parent page "%s" not available, cannot set application %s' % (parent_url,baseurl))
                            return
                        return baseurl
                else:
                    p = app.parent
                    pages = Page.objects.filter(application = p.code, site = self.site)
                    if pages:
                        self.parent = pages[0]
                    else:
                        if messages:
                            messages.error('Parent page not defined %s' % app.code)
                        return
                    url = purl
            else:
                url = self.url_pattern
            
            if self.parent:
                url = '%s%s' % (self.parent.url,url)
            if not url.endswith('/'):
                url += '/'
            if not url.startswith('/'):
                url = '/%s' % url
            return url
        except:
            return None

    def get_children(self):
        '''
        Same as self.children.all()
        return all children of self
        '''
        return Page.objects.filter(parent=self)
    
    def get_next_position(self):
        children = Page.objects.filter(parent=self).order_by('-position')
        return children and (children[0].position+1) or 1

    def get_level(self):
        try:
            url = self.url
            if url.startswith('/'):
                url = url[1:]
            if url.endswith('/'):
                url = url[:-1]
            if url:
                bits  = url.split('/')
                level = len(bits)
            else:
                level = 0
        except:
            level = 1
        return level

    def published(self):
        return self in Page.objects.published()
    published.boolean = True
    
    def additional_head(self):
        return self.additionaldata.filter(where = 1)


    
    
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
        elif blockcontents[-1].plugin_name:
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


class BlockContent(models.Model):
    '''
    A block content object is responsible for mantaining
    relationship between html plugins and their position in page
    '''
    page           = models.ForeignKey(Page,
                                       verbose_name=_("page"),
                                       editable = False,
                                       related_name = 'blockcontents')
    block          = models.PositiveSmallIntegerField(_("block"), editable = False)
    position       = models.PositiveIntegerField(_("position"),
                                                 blank=True,
                                                 editable=False,
                                                 default = 0)
    plugin_name    = models.CharField(blank = True,
                                      max_length = 100)
    arguments      = models.TextField(blank = True)
    container_type = models.CharField(max_length = 30,
                                      blank = False,
                                      verbose_name=_('container'))
    title          = models.CharField(blank = True, max_length = 100)
    
    objects = BlockContentManager()
    
    class Meta:
        unique_together = (('page','block','position'),)
        ordering  = ('page','block','position',)
        
    def __unicode__(self):
        return '%s-%s-%s' % (self.page.id,self.block,self.position)
    
    def htmlid(self):
        return u'blockcontent-%s' % self
    
    def pluginid(self):
        return u'plugin-%s' % self
    
    def __get_plugin(self):
        return get_plugin(self.plugin_name)
    plugin = property(__get_plugin)
        
        
    def _get_wrapper(self):
        return get_wrapper(self.container_type,default_content_wrapper)
    wrapper = property(_get_wrapper)
    
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
        
    def changeform(self, djp):
        f = self.plugin.get_form(djp)
        #, prefix = 'cf_%s' % self.pluginid())
        return formlet(form = f, layout = 'onecolumn',
                       submit = submit(value = 'Change',
                                       name  = 'change_plugin_content'))
    
    def render(self, djp):
        '''
        @param cl: instance of djpcms.views.baseview.ResponseBase
         
        Render the plugin.
        This function is called when the plugin needs to be rendered
        This function call the plugin render function passing three arguments
        '''
        plugin  = self.plugin
        wrapper = self.wrapper
        if plugin:
            djp.add_pluginmedia(plugin)
            #prefix  = 'bd_%s' % self.pluginid()
            prefix = None
            html   = plugin(djp, self.arguments, wrapper = wrapper, prefix = prefix)
            if html:
                return wrapper(djp, self, html)
            else:
                return ''
        else:
            return u''
    
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
        
        

class SiteContentManager(models.Manager):
    
    _cache  = {}
    
    def get_from_code(self, code):
        c = code.lower()
        try:
            return self.__class__._cache[c]
        except:
            try:
                obj = SiteContent.objects.get(code = c)
                if CACHE_VIEW_OBJECTS:
                    self.__class__._cache[c] = obj
                return obj
            except:
                pass
            
    def get_from_codes(self, codes):
        objs = []
        for code in codes:
            obj = self.get_from_code(code)
            if obj:
                objs.append(obj)
        return objs        
    
    def clear_cache(self):
        self.__class__._cache = {}


class SiteContent(models.Model):
    last_modified = models.DateTimeField(auto_now = True, editable = False)
    user_last     = models.ForeignKey(User, null = True, blank = True)
    code          = SlugCode(max_length = 64,
                             unique     = True,
                             help_text  = _("Unique name for the content. Choose one you like"))
    description   = models.TextField(blank = True)
    body          = models.TextField(_('body'),blank=True)
    markup        = models.CharField(max_length = 3, null = False)
    
    objects = SiteContentManager()
    
    def __unicode__(self):
        return u'%s' % self.code
    
    class Meta:
        ordering  = ('code',)
    
    def htmlbody(self):
        text = self.body
        if not text:
            return ''
        mkp = markuplib.get(self.markup)
        if mkp:
            handler = mkp.get('handler')
            text = handler(text)
        return mark_safe(force_unicode(text))
    
    def update(self, user = None, body = ''):
        self.body = body
        user_last = None
        if user and user.is_authenticated():
            user_last = user
        self.user_last = user_last
        self.save()
        
    
def create_new_content(user = None, **kwargs):
    user_last = None
    if user and user.is_authenticated():
        user_last = user
    ct = SiteContent(user_last = user_last, **kwargs)
    ct.save()
    return ct


additional_where = ((1, 'head'),
                    (2, 'body javascript'))

class AdditionalPageData(models.Model):
    page    = models.ForeignKey(Page, related_name = 'additionaldata')
    where   = models.PositiveIntegerField(choices = additional_where, default = 1)
    body    = models.TextField()
    
    def __unicode__(self):
        return self.body
    
    class Meta:
        verbose_name_plural = 'Additional page data'


class Application(models.Model):
    '''
    A general method for creating applications
    '''
    name        = models.CharField(max_length=200, unique = True)
    description = models.TextField(blank = True)
    stylesheet  = models.TextField(blank=True)
    javascript  = models.TextField(blank=True)
    mark        = models.IntegerField(default = 0)
    markup      = models.CharField(max_length = 3, null = False)
    


#mptt.register(Page)
