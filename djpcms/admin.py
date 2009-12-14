from django import forms
from django.contrib import admin

from djpcms import models
from djpcms.forms import PageForm


class BlockContentAdmin(admin.ModelAdmin):
    list_display = ('page','block','position','plugin_name')
    list_filter = ('page', 'block')
    
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('code','last_modified','user_last','markup')
    
class InnerTemplateAdmin(admin.ModelAdmin):
    list_display = ('name','numblocks','blocks','image')

class PageAdmin(admin.ModelAdmin):
    list_display        = ('site','url','application','level','in_navigation','parent',
                           'link','redirect_to','requires_login','inner_template', 'cssinfo',
                           'is_published','module','get_template')
    list_display_links  = ('site','url','application',)
    ordering            = ('site', 'level',)
    list_filter         = ['level']
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
            'fields': ('template', 'code_object')
        }),
        )
    
    search_fields = ('code',)
    
    
admin.site.register(models.SiteContent, SiteContentAdmin)
admin.site.register(models.InnerTemplate, InnerTemplateAdmin)
admin.site.register(models.CssPageInfo, list_display=['id','body_class_name','conteiner_class','fixed'])
admin.site.register(models.Page, PageAdmin)    
admin.site.register(models.BlockContent,    BlockContentAdmin)

