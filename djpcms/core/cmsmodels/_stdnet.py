from datetime import datetime

from stdnet import orm

from djpcms.core.page import PageInterface, BlockInterface, MarkupMixin
from djpcms.utils import htmltype
from djpcms.utils import force_str
from djpcms.template import Template, mark_safe

ModelBase = orm.StdModel
field = orm


class TimeStamp(ModelBase):
    '''Timestamp abstract model class.'''
    last_modified     = field.DateTimeField()
    '''Python datetime instance when ``self`` was last modified.'''
    created           = field.DateTimeField(default = datetime.now)
    '''Python datetime instance when ``self`` was created.'''
    
    class Meta:
        abstract = True
        
    def save(self, commit = True):
        self.last_modified = datetime.now()
        super(TimeStamp,self).save(commit = commit)
    

class InnerTemplate(TimeStamp):
    '''Page Inner template'''
    name     = field.CharField()
    template = field.CharField()
    blocks   = field.CharField()
        
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
    body_class_name      = field.CharField()
    container_class_name = field.CharField()
    fixed    = field.BooleanField(default = True)
    gridsize = field.IntegerField(default = 12)
    
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
    
    
class Site(ModelBase):
    domain = field.SymbolField(unique = True)
    name = field.SymbolField(unique = True)
    
    class Meta:
        app_label = 'djpcms'
        
    def __str__(self):
        return self.name
    
    
class Page(TimeStamp, PageInterface):
    '''The page model holds several information regarding pages in the sitemap.'''
    site        = field.ForeignKey(Site, required = False)
    application_view = field.SymbolField(required = False)
    redirect_to = field.ForeignKey('self',
                                   required  = False,
                                   related_name = 'redirected_from')
    title       = field.CharField()
    url_pattern = field.SymbolField()
    link        = field.CharField()
    inner_template = field.ForeignKey(InnerTemplate, required = False)
    template    = field.CharField()
    in_navigation = field.IntegerField(default=1)
    cssinfo     = field.ForeignKey(CssPageInfo, required = False)
    is_published = field.BooleanField(default=True)
    # Access
    requires_login = field.BooleanField()
    soft_root = field.BooleanField(default=False)
    parent    = field.ForeignKey('self',
                                  required = False,
                                  related_name = 'children')
    doctype = field.IntegerField(default = htmltype.htmldefault)
    insitemap = field.BooleanField(default = True)
    
    # Denormalized level in the tree and url, for performance 
    level       = field.IntegerField(default = 0)
    url         = field.SymbolField()
    application = field.SymbolField(required = False)
    user        = field.SymbolField(required = False)

    class Meta:
        app_label = 'djpcms'

    def __unicode__(self):
        return u'%s%s' % (self.site.domain,self.url)
    
    def save(self, **kwargs):
        self.level = self.get_level()
        super(Page,self).save(**kwargs)

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


class BlockContent(ModelBase, BlockInterface):
    '''A block content object is responsible storing :class:`djpcms.plugins.DJPplugin`
and for maintaining their position in a :class:`djpcms.models.Page`.
    '''
    page           = field.ForeignKey(Page, related_name = 'blockcontents')
    block          = field.IntegerField()
    position       = field.IntegerField(default = 0)
    plugin_name    = field.SymbolField(required = False)
    arguments      = field.CharField()
    container_type = field.SymbolField(required = False)
    title          = field.CharField(required = False)
    for_not_authenticated = field.BooleanField(default = False, index = False)
    requires_login = field.BooleanField(default = False, index = False)
    
    class Meta:
        app_label = 'djpcms'
        

class SiteContent(TimeStamp,MarkupMixin):
    '''Store content for your web site. It can store markup or raw HTML.'''
    user_last     = field.SymbolField(required = False)
    code          = field.SymbolField(unique = True)
    description   = field.CharField()
    body          = field.CharField()
    markup        = field.CharField()
    '''Markup type. If not specified it will be treated as raw HTML.'''
    
    def __str__(self):
        return self.code
    
    class Meta:
        app_label = 'djpcms'
    
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


class AdditionalPageData(ModelBase):
    page    = field.ForeignKey(Page, related_name = 'additionaldata')
    where   = field.IntegerField(default = 1)
    body    = field.CharField()
    
    def __str__(self):
        return self.body
    
    class Meta:
        app_label = 'djpcms'
        
        
class ObjectPermission(ModelBase):
    permission = field.IntegerField(default = 0)
    
    class Meta:
        app_label = 'djpcms'
    

