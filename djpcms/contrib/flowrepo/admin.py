from django.contrib import admin

from flowrepo.models import *
from flowrepo import forms

class ImageInline(admin.TabularInline):
    model = GalleryImage


################################################## FORMS
class ItemAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_display   = ('__unicode__','timestamp', 'content_type', 'url', 'visibility', 'source', 'tags', 'markup', 'allow_comments')
    list_filter    = ('visibility', 'content_type', 'timestamp', 'authors')
    search_fields  = ('name', 'description', 'object_str', 'tags', 'url')
    
    def has_add_permission(self, request):
        return False

class BaseFlowAdmin(admin.ModelAdmin):
    form = forms.FlowForm
    
    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        form.save_model(obj,request.user)
        
class GalleryAdmin(BaseFlowAdmin):
    list_display = ('name','slug')
    
    inlines = [ImageInline]
    
        
class UloaderAdmin(BaseFlowAdmin):
    list_display  = ('slug','name','url')
    form = forms.UploadForm
    
    
class WebAccountAdmin(admin.ModelAdmin):
    list_display = ('name','url','tags','user','e_data')
    search_fields = ('name', 'tags')
    
    
class LinkedAccountAdmin(admin.ModelAdmin):    
    list_display = ('user','provider')

##################################################### REGISTERING
admin.site.register(FlowItem,    ItemAdmin)
admin.site.register(Category,    BaseFlowAdmin, list_display = ('name','slug','type'))
admin.site.register(Report,      BaseFlowAdmin, list_display = ('slug','name'))
admin.site.register(Bookmark,    BaseFlowAdmin, list_display = ('url','name'))
admin.site.register(Message,     BaseFlowAdmin)
admin.site.register(Image,       UloaderAdmin)
admin.site.register(Attachment,  UloaderAdmin)
admin.site.register(Gallery,     GalleryAdmin)
admin.site.register(FlowRelated, list_display = ('item','related'))
admin.site.register(ContentLink, list_display = ('url','identifier'))
admin.site.register(WebAccount,  WebAccountAdmin)
admin.site.register(LinkedAccount, LinkedAccountAdmin)
admin.site.register(CategoryType)
