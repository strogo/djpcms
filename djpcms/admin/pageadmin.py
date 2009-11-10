from django.contrib import admin

from djpcms import models
from djpcms.forms import PageForm, AppPageForm

class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('code','last_modified','user_last','markup')
admin.site.register(models.SiteContent, SiteContentAdmin)

class SiteImageAdmin(admin.ModelAdmin):
    list_display = ('image','code','path','description','url')
admin.site.register(models.SiteImage, SiteImageAdmin)
    
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name','image','blocks')
admin.site.register(models.Template, TemplateAdmin)

admin.site.register(models.CssPageInfo, list_display=['id','body_class_name','conteiner_class','fixed'])

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
    
    #def save_model(self, request, obj, form, change):
    #    url = obj.url_pattern
    #    m = models.CommonUrl(code = url)
    #    try:
    #        m.save()
    #    except:
    #        pass
    #    obj.save()

admin.site.register(models.Page, PageAdmin)

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
admin.site.register(models.AppPage,AppPageAdmin)

