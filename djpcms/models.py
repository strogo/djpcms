import datetime
import re

from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.http import Http404
from django.utils.dateformat import DateFormat
from django.db import models
from django.db.models import Q
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
from djpcms.plugins import wrappergenerator, get_wrapper, \
                           default_content_wrapper, get_plugin, \
                           get_wrapper
from djpcms.utils.models import TimeStamp
from djpcms.utils import lazyattr, function_module
from djpcms.utils.func import PathList
from djpcms.uploads import upload_function, site_image_storage
from djpcms.settings import *

from djpcms import markup

protocol_re = re.compile('^\w+://')


class RootPageDoesNotExist(Exception):
    pass


class PageCache(object):
    
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.root = None
        self.tree = {}
    

class PageManager(models.Manager):
    
    # Cache to avoid re-looking up Page objects all over the place.
    # This cache is shared by all the get_for_* methods.
    _cache  = PageCache()
    
    def get_for_application(self, name):
        return self.get(application = name)
    
    def hierarchy(self, parent=None):
        if parent:
            filter = self.filter(parent=parent)
        else:
            try:
                root = self.root()
            except RootPageDoesNotExist:
                return []
            return [(root, self.hierarchy(root))]
        return [(page, self.hierarchy(page)) for page in filter]
    
    def applications(self):
        return self.sitepages().exclude(app_type = u'')
    
    def sitepage(self, **kwargs):
        site = Site.objects.get_current()
        return self.get(site = site, **kwargs)
    
    def sitepages(self, **kwargs):
        site = Site.objects.get_current()
        return self.filter(site = site, **kwargs)

    def clear_cache(self):
        self.__class__._cache.clear()
        
    def root(self):
        f = self.filter(level=0)
        if f:
            return f[0]
        else:
            return None
        
    def flat_pages(self, **kwargs):
        return self.filter(application = '', **kwargs)
    
    def get_for_model(self, model):
        ct = ContentType.objects.get_for_model(model)
        return self.filter(content_type = ct)

    def published(self):
        try:
            user_logged_in = get_current_user().is_authenticated()
        except:
            user_logged_in = False
        if not user_logged_in:
            qs = self.exclude(requires_login=True)
        else:
            qs = self
        return qs.filter(
                           Q(is_published=True),
                           Q(start_publish_date__lte=datetime.datetime.now()) | Q(start_publish_date__isnull=True), 
                           Q(end_publish_date__gte=datetime.datetime.now()) | Q(end_publish_date__isnull=True),
                           )
    
    def search(self, query, language=None):
        if not query:
            return
        qs = self.published()
        if language:
            qs = qs.filter(
                        Q(title__icontains=query) |
                        Q(pagecontent__language=language) & 
                        (Q(pagecontent__title__icontains=query) |
                        Q(pagecontent__description__icontains=query) |
                        Q(pagecontent__content__icontains=query))
                    )
        else:
            qs = qs.filter(
                        Q(title__icontains=query) |
                        Q(pagecontent__title__icontains=query) |
                        Q(pagecontent__description__icontains=query) |
                        Q(pagecontent__content__icontains=query)
                    )
        return qs.distinct()
    

class InnerTemplate(TimeStamp):
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
    parent      = models.ForeignKey('self',
                                    null  = True,
                                    blank = True,
                                    related_name = 'children',
                                    help_text=_('This page will be appended inside the chosen parent page.'))
    
    code_object = models.CharField(max_length=200,
                                   blank=True,
                                   help_text=_('Optional. Dotted path to a python class dealing with requests'))
        
    # Denormalized level in the tree, for performance 
    level       = models.IntegerField(default = 0, editable = False)

    objects = PageManager()

    class Meta:
        get_latest_by   = 'last_modified'

    def __unicode__(self):
        return u'%s' % self.url
    
    def save(self, **kwargs):
        d = self.get_level()
        self.level = d
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
                return DEFAULT_TEMPLATE_NAME
        else:
            return self.template
    
    def module(self):
        '''
        Same pattern as for get_template
        '''
        if not self.code_object:
            if self.parent:
                return self.parent.module()
            else:
                return DEFAULT_VIEW_MODULE
        else:
            return self.code_object
        
    def object(self, **kwargs):
        '''
        Load a view class and create the view instance
        '''
        code_obj = self.module()
        view = function_module(code_obj)
        return view(self, **kwargs)

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
    
    def modified_url_pattern(self):
        if self.parent:
            return str(self.url_pattern).replace('*','%s')
        else:
            return ''
        
    def num_relative_arguments(self):
        p = str(self.url_pattern)
        if p == '*':
            return 1
        else:
            return 0
        
    @lazyattr
    def num_arguments(self):
        '''
        Return the number of arguments needed by this page
        '''
        p = str(self.url_pattern)
        v = self.num_relative_arguments()
        if self.parent:
            return v + self.parent.num_arguments()
        else:
            return v
        
    def unsafe_url(self):
        if self.application:
            from djpcms.views import appsite
            app = appsite.site.getapp(self.application)
            return u'/%s' % app._regex
        else:
            url = u'/%s' % '/'.join([page.url_pattern for page in self.get_path() if page.parent])
            if not url.endswith('/'):
                url += '/'
            return url

    def get_absolute_url(self):
        try:
            return self.unsafe_url()
        except:
            return 'ERROR'
    url = property(get_absolute_url)

    def get_children(self):
        return Page.objects.filter(parent=self, in_navigation__gt = 0).order_by('in_navigation')
    
    def get_next_position(self):
        children = Page.objects.filter(parent=self).order_by('-position')
        return children and (children[0].position+1) or 1

    def get_level(self):
        try:
            url = self.unsafe_url()
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
    container_type = models.CharField(choices = wrappergenerator(),
                                      default = default_content_wrapper.name,
                                      max_length = 30,
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
            #prefix  = 'bd_%s' % self.pluginid()
            prefix = None
            html   = plugin(djp, self.arguments, wrapper = wrapper, prefix = prefix)
            return wrapper(djp, self, html)
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
    markup        = models.CharField(max_length = 3,
                                     choices = markup.choices(),
                                     default = markup.default(),
                                     null = False)
    
    objects = SiteContentManager()
    
    def __unicode__(self):
        return u'%s' % self.code
    
    class Meta:
        ordering  = ('code',)
    
    def htmlbody(self):
        text = self.body
        if not text:
            html = u''
        mkp = markup.get(self.markup)
        if mkp:
            handler = mkp.get('handler')
            html = force_unicode(handler(text))
        return mark_safe(html)
    
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


class Application(models.Model):
    '''
    A general method for creating applications
    '''
    name        = models.CharField(max_length=200, unique = True)
    description = models.TextField(blank = True)
    stylesheet  = models.TextField(blank=True)
    javascript  = models.TextField(blank=True)
    mark        = models.IntegerField(default = 0)
    markup      = models.CharField(max_length = 3,
                                   choices = markup.choices(),
                                   default = markup.default(),
                                   null = False)
    
    
    