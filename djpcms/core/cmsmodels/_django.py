import datetime
import re
import sys
import logging

from django.utils.dateformat import DateFormat
from django.db import models
from django.utils import html, translation
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from djpcms.template import Template, mark_safe
from djpcms.core.page import PageInterface, BlockInterface
from djpcms.permissions import has_permission, get_view_permission
from djpcms.fields import SlugCode
from djpcms.plugins import get_wrapper, default_content_wrapper, get_plugin
from djpcms.utils import lazyattr, function_module, force_str, htmltype
from djpcms.utils.func import PathList
from djpcms.uploads import uploader, storage_manager
import djpcms.contrib.flowrepo.markups as markuplib

from .djmanagers import PageManager, BlockContentManager, SiteContentManager, PermissionManager


protocol_re = re.compile('^\w+://')


class TimeStamp(models.Model):
    '''Timestamp abstract model class.'''
    last_modified     = models.DateTimeField(auto_now = True)
    '''Python datetime instance when ``self`` was last modified.'''
    created           = models.DateTimeField(auto_now_add = True)
    '''Python datetime instance when ``self`` was created.'''
    
    class Meta:
        abstract = True
    

class InnerTemplate(TimeStamp):
    '''Page Inner template'''
    name     = models.CharField(max_length = 200)
    image    = models.ImageField(upload_to = uploader('template'),
                                 storage = storage_manager('template'),
                                 null = True, blank = True)
    template = models.TextField(blank = True)
    blocks   = models.TextField(help_text = _('comma separated strings indicating the content blocks'))
        
    def __unicode__(self):
        return u'%s' % self.name
    
    class Meta:
        app_label = 'djpcms'
    
    def render(self, c):
        '''Render the inner template given the context ``c``.
        '''
        return Template(self.template).render(c)
        
    def numblocks(self):
        '''Number of ``blocks`` within template.'''
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
        app_label = 'djpcms'
        
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
    
    
class Page(TimeStamp, PageInterface):
    '''The page model holds several information regarding pages in the sitemap.'''
    site        = models.ForeignKey(Site)
    '''Site to which the page belongs.'''
    application_view = models.CharField(max_length = 200, blank = True)
    '''Name of the :class:`djpcms.views.appview.AppViewBase` owner of the page. It can be empty, in which case the page is a ``flat`` page (not part of an application).'''
    redirect_to = models.ForeignKey('self',
                                    null  = True,
                                    blank = True,
                                    related_name = 'redirected_from')
    title       = models.CharField(max_length = 60,
                                   blank = True,
                                   help_text=_('Optional. Page Title.'))
    
    url_pattern = models.CharField(max_length = 200,
                                   blank = True,
                                   help_text=_('URL bit. No slashes.'))
    
    link        = models.CharField(max_length = 60,
                                   blank = True,
                                   help_text=_('Short name to display as link to this page.'),
                                   verbose_name = 'link name')
    
    inner_template = models.ForeignKey(InnerTemplate,
                                       null = True,
                                       blank = True,
                                       verbose_name=_("inner template"))
    '''Page inner template is an instance of :class:`djpcms.models.InnerTemplate`. It contains information regrading the number of ``blocks`` in the page
as well as the layout structure.'''
    
    template    = models.CharField(max_length=200,
                                   verbose_name = 'template file',
                                   null = True,
                                   blank = True,
                                   help_text=_('Optional. Templale file for the page.'))
    '''Optional template file for rendering the page.
If not specified the :setting:`DEFAULT_TEMPLATE_NAME` is used.'''
    
    in_navigation = models.PositiveIntegerField(default=1,
                                                verbose_name = _("Position"),
                                                help_text = _("Position in navigation. If 0 it won't be in navigation. If bigger than 100 it will be a secondary navigation item."))
    '''Integer flag indicating positioning in the site navigation (see :class:`djpcms.utils.navigation.Navigator`). If set to ``0`` the page won't be displayed in the navigation.'''
    
    cssinfo     = models.ForeignKey(CssPageInfo,
                                    null = True,
                                    blank = True,
                                    verbose_name='Css classes')
    
    is_published = models.BooleanField(default=True,
                                       help_text=_('Whether or not the page is accessible from the web.'),
                                       verbose_name='published')
    # Access
    requires_login = models.BooleanField(verbose_name = _('login required'))
       
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
    '''Parent page. If ``None`` the page is the site ``root`` page.'''
    
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
    application = models.CharField(max_length = 200, blank = True)
    '''Name of the :class:`djpcms.views.appsite.ApplicationBase` owner of the page. It can be empty, in which case the page is a ``flat`` page (not part of an application).'''
    user        = models.ForeignKey(User, null = True, blank = True)

    objects = PageManager()

    class Meta:
        app_label = 'djpcms'
        get_latest_by   = 'last_modified'
        verbose_name_plural = "Sitemap"

    def __unicode__(self):
        return u'%s%s' % (self.site.domain,self.url)
    
    def save(self, **kwargs):
        self.level = self.get_level()
        super(Page,self).save(**kwargs)

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
    
    def numblocks(self):
        t = self.inner_template
        return 0 if not t else t.numblocks()
    
    def create_template(self, name, template, blocks):
        t = InnerTemplate(name = name,
                          template = template,
                          blocks = blocks)
        t.save()
        return t
    
    def _get_block(self, block, position = None):
        blocks = BlockContent.objects.filter(page = self, block = block)
        N = blocks.count()
        if position == None:
            b = BlockContent(page = self,block = block,position = N)
            b.save()
            return b
        else:
            return blocks.get(position = position)



class BlockContent(models.Model, BlockInterface):
    '''A block content object is responsible storing :class:`djpcms.plugins.DJPplugin`
and for maintaining their position in a :class:`djpcms.models.Page`.
    '''
    page           = models.ForeignKey(Page,
                                       verbose_name=_("page"),
                                       editable = False,
                                       related_name = 'blockcontents')
    ''':class:`djpcms.models.Page` holding ``self``.'''
    block          = models.PositiveSmallIntegerField(_("block"), editable = False)
    '''Integer indicating the block number within the page.'''
    position       = models.PositiveIntegerField(_("position"),
                                                 blank=True,
                                                 editable=False,
                                                 default = 0)
    '''Integer indicationg the position of content within the content ``block``.'''
    plugin_name    = models.CharField(blank = True,
                                      max_length = 100)
    '''The unique :attr:`djpcms.plugins.DJPplugin.name` of plugin in the content ``block``.'''
    arguments      = models.TextField(blank = True)
    ''':class:`djpcms.plugins.DJPplugin` arguments as JSON string.'''
    container_type = models.CharField(max_length = 30,
                                      blank = False,
                                      verbose_name=_('container'))
    '''The unique :attr:`djpcms.plugins.DJPwrapper.name` of the plugin html-wrapper.'''
    title          = models.CharField(blank = True, max_length = 100)
    '''Optional title'''
    for_not_authenticated = models.BooleanField(default = False)
    '''If ``True`` (default is ``False``) the block will be rendered **only** for non-authenticated users.'''
    requires_login = models.BooleanField(default = False)
    '''If ``True`` (default is ``False``) the block will be rendered **only** for authenticated users.'''
    objects = BlockContentManager()
    
    class Meta:
        app_label = 'djpcms'
        unique_together = (('page','block','position'),)
        ordering  = ('page','block','position',)
        permissions = (
            ("view_blockcontent", "Can view block content"),
        )
    
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


class SiteContent(models.Model):
    '''Store content for your web site. It can store markup or raw HTML.'''
    last_modified = models.DateTimeField(auto_now = True, editable = False)
    user_last     = models.ForeignKey(User, null = True, blank = True)
    code          = SlugCode(max_length = 64,
                             unique     = True,
                             help_text  = _("Unique name for the content. Choose one you like"))
    description   = models.TextField(blank = True)
    body          = models.TextField(_('body'),blank=True)
    markup        = models.CharField(max_length = 3, blank = True, null = False)
    '''Markup type. If not specified it will be treated as raw HTML.'''
    
    objects = SiteContentManager()
    
    def __unicode__(self):
        return u'%s' % self.code
    
    class Meta:
        app_label = 'djpcms'
        ordering  = ('code',)
    
    def htmlbody(self):
        text = self.body
        if not text:
            return ''
        mkp = markuplib.get(self.markup)
        if mkp:
            handler = mkp.get('handler')
            text = handler(text)
            text = mark_safe(force_str(text))
        return text
    
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
        app_label = 'djpcms'
        verbose_name_plural = 'Additional page data'


class ObjectPermission(models.Model):
    '''Model for handling per-object permissions.
An object which has at least one of this model instances associated with, will
have permissions handled by this model only.'''
    user = models.ForeignKey(User, verbose_name=_(u"User"), blank=True, null=True)
    group = models.ForeignKey(Group, verbose_name=_(u"Group"), blank=True, null=True)
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"))

    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name = 'objectpermissions')
    content_id = models.PositiveIntegerField(verbose_name=_(u"Content id"))
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    
    objects = PermissionManager()

    class Meta:
        app_label = 'djpcms'
        
    def has_perm(self, user):
        '''Check permission for user'''
        if self.user:
            return self.user == user
        else:
            return user.groups.filter(id = self.group.id).count() > 0