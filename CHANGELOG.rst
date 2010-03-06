
0.6 beta
=======================
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
 
0.4 (2009-12-24)
=====================
first official Alpha release.

0.5 (2010-01-13)
=====================

 * Bug fixes
 * Added "splitregex" named options in views.appview.AppView constructor 
 * Added DISQUS in plugins
 * Removed StaticPagesMiddleware request handler
 * response method in djpcmsview class has been replaced with __call__ method
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
 
0.4 (2009-12-24)
=====================
first official Alpha release.
