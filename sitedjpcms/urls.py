from django.conf.urls.defaults import patterns
from django.conf import settings
from djpcms.urls import site_urls


urlpatterns = patterns('', *site_urls)



