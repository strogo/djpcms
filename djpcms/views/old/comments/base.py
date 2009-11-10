from django.conf.urls.defaults import *

from djpcms.views.wrapview import nopageview


def get_commenturls(baseurl = 'comments'):
    return (r'^%s/' % baseurl, include('djpcms.views.comments.urls')),    

