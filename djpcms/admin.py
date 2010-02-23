from django import forms, template, http
from django.forms.forms import pretty_name
from django.contrib import admin
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.encoding import force_unicode
#from django.views.decorators.csrf import csrf_protect
#from django.contrib.admin.util import display_for_field, label_for_field

from djpcms import models
from djpcms.forms import PageForm
from djpcms.utils.ajax import simplelem

class AdditionalPageDataInline(admin.TabularInline):
    model = models.AdditionalPageData
    
class BlockContentAdmin(admin.ModelAdmin):
    list_display = ('page','block','position','plugin_name')
    list_filter = ('page', 'block')
    
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('code','last_modified','user_last','markup')
    
class InnerTemplateAdmin(admin.ModelAdmin):
    list_display = ('name','numblocks','blocks','image')

class PageAdmin(admin.ModelAdmin):
    list_display        = ('url','application','in_navigation','link','redirect_to','requires_login','inner_template', 'cssinfo',
                           'is_published','get_template')
    inlines             = [AdditionalPageDataInline]
    save_on_top         = True
    form                = PageForm
    
    fieldsets = (
        (None, {
            'fields': ('site', 'application', 'parent', 'title', 'url_pattern',
                       'link', 'inner_template', 'in_navigation', 'cssinfo')
        }),
        ('Authentication', {
            'classes': ('collapse',),
            'fields': ('requires_login', 'is_published', 'redirect_to')
        }),
        ('Custom', {
            'classes': ('collapse',),
            'fields': ('doctype', 'soft_root', 'template',)
        }),
        )
    
    search_fields = ('code',)
    
    def _addpage(self, cl, pd, pg, url, state = 'closed'):
        children = []
        qs = pg.get_children()
        if qs:
            ctx = {'state': state,
                   'children': children}
        else:
            ctx = {}        
        data = [{'title': url}]
        for field_name in self.list_display[1:]:
            header = cl.lookup_opts.get_field(field_name)
            #header = label_for_field(field_name, cl.model, model_admin = cl.model_admin, return_attr = False)
            val = getattr(pg,field_name,None)
            if callable(val):
                val = val()
            if val == None:
                val = ''
            data.append(str(val))
        ctx['data'] = [{'name': 'default', 'data': data}]
        pd.append(ctx)
        for pg in qs:
            url = pg.url[1:]
            self._addpage(cl, children, pg, url)
        
    def changelist_view(self, request, extra_context=None):
        if request.is_ajax():
            ChangeList = self.get_changelist(request)
            cl = ChangeList(request, self.model, self.list_display, self.list_display_links, self.list_filter,
                            self.date_hierarchy, self.search_fields, self.list_select_related,
                            self.list_per_page, self.list_editable, self)
            sites = []
            for site in Site.objects.all():
                pages = cl.query_set.filter(site = site)
                if pages:
                    root = pages.filter(level=0)[0]
                    url  = site.domain + root.url
                    self._addpage(cl, sites, root, url, 'open')
            
            cols = ['url']
            for field_name in self.list_display[1:]:
                header = cl.lookup_opts.get_field(field_name)
                #header = label_for_field(field_name, cl.model, model_admin = cl.model_admin, return_attr = False)
                cols.append(pretty_name(header))
            js = simplelem({'sites': sites,
                            'columns': cols})
            return http.HttpResponse(js.dumps(), mimetype='application/javascript') 
        else:
            return super(PageAdmin,self).changelist_view(request, extra_context)
                
    
admin.site.register(models.SiteContent, SiteContentAdmin)
admin.site.register(models.InnerTemplate, InnerTemplateAdmin)
admin.site.register(models.CssPageInfo, list_display=['id','body_class_name','conteiner_class','fixed'])
admin.site.register(models.Page, PageAdmin)    
admin.site.register(models.BlockContent,    BlockContentAdmin)
admin.site.register(models.DeploySite, list_display=['user','created','comment'])
