from django.contrib import admin

from djpcms.contrib.social.models import LinkedAccount



class LinkedAccountAdmin(admin.ModelAdmin):    
    list_display = ('user','provider')
    
    
admin.site.register(LinkedAccount, LinkedAccountAdmin)