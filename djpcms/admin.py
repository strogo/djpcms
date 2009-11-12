from django import forms
from django.contrib import admin

from djpcms import models
from djpcms.plugins.snippet.models import Snippet
from djpcms.forms import PageForm, AppPageForm


class BlockContentAdmin(admin.ModelAdmin):
    list_display = ('page','block','position','plugin_name','plugin','container_type')
    
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('code','last_modified','user_last','markup')
    
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ('image','code','path','description','url')

class PageAdmin(admin.ModelAdmin):
    list_display        = ('site','code','level','in_navigation',
                           'absolute_url','parent',
                           'href_name','redirect_to','requires_login',
                           'is_published','module','get_template')
    list_display_links  = ('code',)
    prepopulated_fields = {'url_pattern':('code',), 'href_name':('code',)}
    ordering            = ('site', 'level', 'code',)
    list_filter         = ['level']
    save_on_top         = True
    form                = PageForm
    
    fieldsets = (
        (None, {
            'fields': ('site', 'parent', 'code', 'title', 'url_pattern',
                       'href_name', 'code_object', 'template',
                       'inner_template', 'in_navigation','cssinfo')
        }),
        ('Authentication', {
            'classes': ('collapse',),
            'fields': ('requires_login', 'is_published', 'redirect_to')
        }),
        )
    
    search_fields = ('code',)

class AppPageAdmin(admin.ModelAdmin):
    list_display = ('site', 'code', 'in_navigation','href_name','title',
                    'inner_template', 'get_template')
    ordering  = ('code',)
    fieldsets = (
        (None, {
            'fields': ('site', 'code', 'title', 'href_name',
                       'inner_template', 'cssinfo',
                       'in_navigation', 'redirect_to')
        }),
        )
    form = AppPageForm
    
    
admin.site.register(models.SiteContent, SiteContentAdmin)
admin.site.register(models.SiteImage, SiteImageAdmin)
admin.site.register(models.Template, list_display = ['name','image','blocks'])
admin.site.register(models.CssPageInfo, list_display=['id','body_class_name','conteiner_class','fixed'])
admin.site.register(models.Page, PageAdmin)    
admin.site.register(models.AppPage,AppPageAdmin)
admin.site.register(models.BlockContent,    BlockContentAdmin)
admin.site.register(models.AppBlockContent, BlockContentAdmin)

admin.site.register(Snippet)
