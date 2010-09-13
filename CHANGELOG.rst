
Version 0.8.a2
==============================
 * Reregistering a model to ``djpcms.views.appsite.site`` won't raise any error. It overrides the previous model application.
 * Included ``examples`` directory in the package compressed file.
 * Refactored autocomplete with tests.
 * **11 unit tests**.
 
 
Version 0.7.2 (2010-Sep-07)
==============================
 * Fixed few missing elements in :file:`setup.py`.
 * This is the first ``alpha`` release of the **0.8 version**. Several new functionalities as well as a more robust codebase.
 * Removed a couple of obsolete functions in :class:`djpcms.views.response.DjpResponse` and added the new function ``instancecode`` to return an unique code for an instance of a model.
 * Added ``form_template`` in :class:`djpcms.views.appsite.ModelApplication` for customizing :ref:`uniforms <topics-utils-uniform>` rendering.
 * Updated to jQuery 1.4.2 and added two jQuery UI themes.
 * Added :setting:`DJPCMS_STYLE` setting for specifying ``css`` style.
 * :class:`djpcms.views.cache.PageCache` works when django sessions are not available. Previously it was failing.
 * Added ``AUTHORS`` to base directory and included ``jogging`` in contrib.
 * Removed ``settings`` import in ``utils.navigation``.
 * Created the ``djpcmstest`` in the ``examples`` directory. This example is used to create pages for ``unittests``. 
 * Removed obsolete code in ``plugins``.
 * ``DocView`` refactoring and documentation.
 * ``uniforms`` refactoring and documentation.
 * Unified ``ApplicationBase`` and ``ModelApplication``. They now are of the same ``ApplicationMetaClass`` type.
 * Moved the ``user`` application into ``views.appsite.apps`` for consistency.
 * Renamed ``docview`` as ``docs`` and moved into the ``views.appsite.apps`` directory.
 * **9 unit tests**. 
 
 
Version 0.7.1 (2010-Aug-24)
==============================
 * Default value for setting ``SERVE_STATIC_FILES`` is set to ``True``.
 * Critical bug fix in :class:`siro.plugins.text.Text` which was crashing the edit form.


Version 0.7.0 (2010-Aug-19)
===================================
 * Backward incompatible changes to internal modules. To use this version, changes needs to be made when importing ``djpcms`` modules.
 * Added more documentation which is hosted at http://packages.python.org/djpcms/
 * ``uniforms`` moved from ``djpcms.utils.uniforms``.
 * Added ``list_per_page`` attribute to ``ModelApplication``.


Version 0.6.3 (2010-Jun-06)
========================================
 * Added rightclickmenu jQuery plugin.
 * Fixed missing data in ``setup.py``.
 * ``Memcached`` monitor-plugin displays MegaBytes used.


Version 0.6.2 (2010-May-07)
========================================
 * Several bug fixes.
 * Application views can specify several ajax views by passing a dictionary called ``ajax_view``.


Version 0.6.1 (2010-Apr-30) 
========================================
 * Added ``utils.unipath`` from http://pypi.python.org/pypi/Unipath
 * Added ``ajax`` property to ``uniforms.FormHelper`` class


Version 0.6 (2010-Apr-24)
=======================================
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

 
Version 0.5 (2010-Jan-13)
===================================

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

 
Version 0.4 (2009-Dec-24)
=========================================

 * First official Alpha release.

 