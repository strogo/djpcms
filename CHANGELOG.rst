
0.6.3
====================
 * Added rightclickmenu jQuery plugin
 * Fixed missing data in setup.py
 * Memcached monitor displays MB used.

0.6.2 (2010-May-07)
====================
 * Minor bug fixes
 * Application views can specify several ajax views by passing a dictionary called `ajax_view`

0.6.1 (2010-Apr-30) 
====================
 * Added `utils.unipath` from http://pypi.python.org/pypi/Unipath
 * Added ajax property to uniform helper class

0.6 (2010-Apr-24)
==================
 * Added `autocomplete` and `uniform` in `utils.html`
 * `ModelApplication` and `DJPplugin` metaclasses derive from `forms.MediaDefiningClass`
 * Added color picker jquery plugin from http://www.eyecon.ro/colorpicker/
 * When serving media files add applications media roots in `urls`
 * Added `list_display` a la django admin in `views.appsite` so that lists of objects can be displayed as a table.
 * Added tablesorter jQuery plugin from http://tablesorter.com
 * Added `compress_if_you_can` template tag for compressing media files using third party libraries.
 * Added `django-compressor` to contrib.
 * Started decoupling from django. Still very much a django app right now.
 * Compatible with django 1.2 and multidatabase
 * Bug in views.apps.flowrepo.appurl.FlowRepoApplication.has_permission fixed.
 * TagArchiveView title overwritten
 * moved to jQuery 1.4.1
 * Added swfobject in media
 * added jstree from http://www.jstree.com/
 * Added jquery.pagination for pagination of search results
 * Introduced the pagecache object for caching Pages
 * Sitemap handled by pagecache. For now only static pages and application pages without arguments are included.
 * Added lloogg_analytics and css_validators in template tags
 * NEW FIELD IN PAGE MODEL!! Added doctype field for specifying document type (HTML 4.01, XHTML 1, HTML 5)
 * NEW FIELD IN PAGE MODEL!! Added insitemap for disabling a page from sidemap and robots
 * Refactored search form plugin - django form compatible template
 * Added autocomplete-off javascript decorator - so that xhtml validates
 * url resolver split between main urls and sub-applications
 * Better title in flowrepo contentview
 
0.5 (2010-Jan-13)
=====================

 * Bug fixes
 * Added "splitregex" named options in views.appview.AppView constructor 
 * Added DISQUS in plugins
 * Removed StaticPagesMiddleware request handler
 * Response method in djpcmsview class has been replaced with __call__ method
 * Change in urls
 * Added DeploySite model
 * Added Deploy plugin
 * Added jquery.cicle in media. jQuery plugin to handle rotating pictures.
 * Added plugin's url for handling dynamic plugins not connected to a model.
 * Added Contact form plugin.
 * ADDED NEW MODEL AdditionalPageData for injecting ad-hoc data into page head or javascript in page body
 * Content text plugin is now wrapped into a div with class 'djpcms-text-content'.
 * Breadcrumbs name is given by view title
 * Created the DjpResponse object in views.response.
 
0.4 (2009-Dec-24)
=====================

 * First official Alpha release.

 