import datetime
import re

from django.utils.safestring import mark_safe
from django.http import Http404
from django.utils.dateformat import DateFormat
from django.db.models import Q
from django.utils import translation
from django.utils import html
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.datastructures import SortedDict
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.template import Template as DjangoTemplate

#from djcms.middleware.threadlocals import get_current_user
from djpcms.utils import lazyattr, function_module
from djpcms.uploads import upload_function, site_image_storage
from djpcms.settings import *

from base import *

protocol_re = re.compile('^\w+://')



__all__ = ['Page',
           'Template',
           'CssPageInfo',
           'RootPageDoesNotExist',
           'UserPage']


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
        root = self.__class__._cache.root
        if not root:
            try:
                root = self.filter(parent__isnull=True, site = Site.objects.get_current())[0]
                if CACHE_VIEW_OBJECTS:
                    self.__class__._cache.root = root
            except IndexError:
                raise RootPageDoesNotExist, unicode(_('Please create at least one page.'))
        return root
    
    def get_for_code(self, code):
        page = self.__class__._cache.tree.get(code,None)
        if not page:
            try:
                page = self.get(code = code)
                if CACHE_VIEW_OBJECTS:
                    self.__class__._cache.tree[code] = page
            except:
                page = None
        return page
    
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
    



class Template(TimeStamp):
    name     = models.CharField(max_length = 200)
    image    = models.ImageField(upload_to = upload_function, storage = site_image_storage(), null = True, blank = True)
    template = models.TextField(blank = True)
    blocks   = models.TextField(help_text = _('comma separated strings indicating the content blocks'))
    
    class Meta:
        app_label = current_app_label
        
    def __unicode__(self):
        return u'%s' % self.name
    
    def render(self, c):
        t = DjangoTemplate(self.template)
        return t.render(c)
        
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
    
    class Meta:
        app_label = current_app_label
        
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




class UserPage(models.Model):
    user      = models.ForeignKey(User)
    public    = models.BooleanField(default = True)
    
    class Meta:
        app_label = current_app_label
    
    
    
class PageBase(TimeStamp):
    site        = models.ForeignKey(Site)
    redirect_to = models.ForeignKey('self',
                                    null  = True,
                                    blank = True,
                                    related_name = 'redirected_from')
    title       = models.CharField(max_length = 60, blank = True,
                                   help_text=_('Optional. Page Title.'))
    
    href_name   = models.CharField(max_length = 200, blank = True,
                                   help_text=_('The name of the link to this page.'),
                                   verbose_name = 'link name')
    
    inner_template = models.ForeignKey(Template, verbose_name=_("inner template"))
    
    template    = models.CharField(max_length=200,
                                   verbose_name = 'template file',
                                   null = True,
                                   blank = True,
                                   help_text=_('Optional. Templale file for the page.'))
    
    in_navigation = models.PositiveIntegerField(default=1,
                                                help_text = _("Position in navigation. If 0 it won't be in navigation"))
        
    cssinfo     = models.ForeignKey(CssPageInfo, null = True, blank = True, verbose_name='Css classes')
    
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
    
    typenum     = 0
    
    class Meta:
        abstract = True
        
    def numblocks(self):
        return self.inner_template.numblocks()
        
    
class Page(PageBase):
    code        = SlugCode(max_length=32,
                           help_text=_('The unique page code. Choose one you like'))
    url_pattern = models.CharField(max_length = 200,
                                   help_text=_('The name of the page that appears in the URL.'))
    # Navigation
    parent      = models.ForeignKey('self',
                                    null  = True,
                                    blank = True,
                                    related_name = 'children_pages',
                                    help_text=_('This page will be appended inside the chosen parent page.'))
    
    code_object = models.CharField(max_length=200,
                                   null=True,
                                   blank=True,
                                   help_text=_('Optional. Dotted path to a python class dealing with requests'))
    
    # hidden fields
    level       = models.IntegerField(default = 0, editable = False)

    objects = PageManager()

    class Meta:
        app_label       = current_app_label
        #unique_together = ('site','code')
        unique_together = (('site','url_pattern','parent'),
                           ('site','code'))
        get_latest_by   = 'last_modified'

    def __unicode__(self):
        #return u'%s - %s' % (self.site,self.code)
        return u'%s' % self.code
    
    def save(self, **kwargs):
        Page.objects.clear_cache()
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

    def get_absolute_url(self):
        '''
        Calculate the absolute url for the page
        '''
        url = u'/%s' % '/'.join([page.url_pattern for page in self.get_path() if page.parent])
        if not url.endswith('/'):
            url += '/'
        return url
    absolute_url = property(fget = get_absolute_url)

    def get_children(self):
        return Page.objects.filter(parent=self, in_navigation__gt = 0).order_by('in_navigation')
    
    def get_next_position(self):
        children = Page.objects.filter(parent=self).order_by('-position')
        return children and (children[0].position+1) or 1

    def get_level(self):
        parent = self.parent
        level = 0
        while parent:
            level += 1
            parent = parent.parent
        return level

    def published(self):
        return self in Page.objects.published()
    published.boolean = True
    
    