from django.contrib import admin
from djpcms.contrib.logdb.models import Log

class LogAdmin(admin.ModelAdmin):
    date_hierarchy = 'datetime' 
    model = Log
    list_display = ['datetime', 'host', 'level', 'source', 'user', 'client', 'abbrev_msg']
    search_fields = ['source', 'msg', 'host']
    list_filter = ['level', 'datetime', 'source', 'user', 'client', 'host']

admin.site.register(Log, LogAdmin)
