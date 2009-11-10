from django import forms
from django.contrib import admin
from djpcms.models import BlockContent, AppBlockContent
from djpcms.plugins.snippet.models import Snippet



class BlockContentAdmin(admin.ModelAdmin):
    list_display = ('page','block','position','plugin_name','plugin','container_type')
admin.site.register(BlockContent,    BlockContentAdmin)
admin.site.register(AppBlockContent, BlockContentAdmin)

admin.site.register(Snippet)