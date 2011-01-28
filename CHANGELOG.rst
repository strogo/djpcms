
Version 1.0.0 - Development
=======================================
* **BACKWARD INCOMPATIBLE CHANGES**
* This is the first release not dependent on ``django``.
* Object Relational mapping can be done with ``django`` or ``python-stdnet`` or none of them.
* Other ORMs can be registered to the library::

    from djpcms import sites
    
    sites.register_orm('path.to.my.ormwrapper')
    
* Introduced new Ajax decorator ``rearrange`` which adds drag & drop
  functionalities during page editing.
* Added abstraction for ``User``, ``Request`` and ``Response`` classes.
* Added ``save as new`` functionality to :class:`djpcms.views.appview.EditView`.
* Added `rst` markup handled by sphinx_ in :mod:`djpcms.contrib.flowrepo.markups` module.
* Added ``getdata`` function to ``DjpResponse`` as the preferred way to extract data from the response object.
  In this way it is guaranteed the response object is initialised properly.
* ``forms.LazyChoiceField`` replaced by ``forms.ChoiceField``, lazy by default.
* Added :meth:`djpcms.views.appsite.Application.get_label_for_field`.
* Added a :mod:`middleware` module for logging when using ``django`` version less than ``1.3``.
* Renamed ``ApplicationBase`` as :class:`djpcms.views.appsite.Application``.
* Two of many steps towards a ``django`` free ``djpcms``. You don't need to specify ``settings`` file if you don't want to,
  and no need to specify the ``ROOT_URLCONF`` either. Thanks to the :mod:`djpcms.core.defaults`.
  Refreshing.
* Redesign of the test suite so that several different applications can be tested.
* Applications can be reloaded at runtime. Useful for testing, but maybe more.
* Injecting the instance or ``None`` of current ``url`` into ``request`` object.
* Added more docs on views and applications.
* Added :mod:`djpcms.contrib.social` application with ``OAuth``. Still in ``alpha``.
* **74 unit tests**. Coverage **51%**.

Version 0.8.5 (2010-Nov-16)
=======================================
* Added ``object_links`` function and ``exclude_object_links``
  attribute in :class:`djpcms.views.appsite.ModelApplication`.
* Ajax delete views display a confirmation dialog box.
* Added :mod:`djpcms.contrib.flowrepo` module. Still experimental, not ready for production.
* Added django-tagging_ to ``libs`` module. A fall back when not available in the PYTHONPATH.
* **42 unit tests**.

Version 0.8.4 (2010-Nov-07)
=============================
* Added :mod:`djpcms.views.apps.contactus` module which implements a "Contact Us" application. Nice and simple.
* Refactoring of :func:`djpcms.views.baseview.get_page` function.
* The :attr:`djpcms.views.appview.AppViewBase.name` attribute is given by the attribute name in the application. For example::

	class MyApp(appsite.ModelApplication):
	    add = appview.AddView()
	    
  The name of the only view in ``MyApp`` is ``add``.
* Added :func:`djpcms.views.response.DjpResponse.has_own_page` function to check if a response has its own page object (rather than the ancestor one).
* Added :attr:`djpcms.models.Page.application_view` field.
* Page url calculation moved into form validation.
* Added :attr:`djpcms.views.appview.AppViewBase.plugin_form` attribute used to specify the :attr:`djpcms.plugins.DJPplugin.form` for an application view.
* Added :mod:`djpcms.core.models` module for handling models from different libraries/frameworks.
  :class:`djpcms.views.appsite.ModelApplication` can handle database models other than ``Django``.
* More documentation.
* **42 unit tests**.

Version 0.8.3 (2010-Oct-18)
=================================
* Added :class:`djpcms.models.ObjectPermission` model for handling granular permissions at object level.
  To use the new permissions add::
  
  		AUTHENTICATION_BACKENDS = (
  		    'djpcms.permissions.Backend',
		)
		
  in the ``settings`` file.
  
* Added :attr:`djpcms.models.BlockContent.requires_login` boolean field.
  If set to ``True`` (default is ``False``) the content block will be displayed **only**
  to authenticated users.
* Added :attr:`djpcms.models.BlockContent.for_not_authenticated` boolean field.
  If set to ``True`` (default is ``False``) the content block will be displayed **only**
  to non authenticated users.
* Added ``yui-simple3.html`` template to ``templates/djpcms/yui`` directory.
* :class:`djpcms.utils.uniforms.FormLayout` injects its ``default_style`` to
  :class:`djpcms.utils.uniforms.UniFormElement` instances without a style class defined.
* **38 unit tests**.

Version 0.8.2 (2010-Oct-10)
==============================
* bug fixes
* **38 unit tests**.

Version 0.8.1 (2010-Oct-06)
==============================
* :attr:`djpcms.models.Page.in_navigation` overrides application default.
* Relaxed :class:`djpcms.forms.PageForm` validation by allowing several defaults.
  To create a flat page you can simply pass a ``url_pattern``.
* Added support for multiple Pages in application views with parameters (such as the object view).
  This is a very important addition which allows applications with input parameters
  to have different pages for different parameters. In other words, a database objects can have
  its own page if required.
* Added a post save :class:`djpcms.models.Page` signal in :mod:`djpcms.views.cache`
  to clear the page cache after every page database update.
* :meth:`djpcms.utils.uniforms.UniForm.render` passes ``inputs`` into :meth:`djpcms.utils.uniforms.FormLayout.render`. Useful for custom layouts. 
* :attr:`djpcms.views.appsite.ModelApplication.form_template` attribute can be a callable.
* :meth:`djpcms.views.appsite.ModelApplication.get_form` add a class name to the form equal to ``appname-modelname``.
* **38 unit tests**.


Version 0.8 (2010-Sep-30)
==============================
* **BACKWARD INCOMPATIBLE CHANGES**
* To use this version, changes needs to be made when importing the :mod:`djpcms.urls` module.
  Your site ``urls`` file can simply be::
	
	from djpcms.urls import *
	urlpatterns = site_urls.patterns()

* http://djpcms.com has gone live!
* Three working examples. One is running http://djpcms.com, one is the subject of the tutorial and one is used for testing. 
* If no pages are available in the database a root page is created by the framework.
* Phased out ``form.py`` in ``djpcms.utils.html`` module.
* Migrations included in the source. Compatible with South_.
* HTML plugin removed. Raw html is handled by the :class:`djpcms.plugins.text.Text` plugin when no markup is selected.
* Introduced :attr:`djpcms.views.apps.docs.DocApplication.master_doc` attribute for specifying the master document of sphinx.
* Fixed a silly bug in inline editing. The delete link did not have the ``ajax`` class.
* Documentation and tests for :mod:`djpcms.contrib.jdep`.
* Added :setting:`DJPCMS_STYLING_FUNCTION` setting for specifying custom styles.
* Added :setting:`DJPCMS_SITE_MAP` setting to opt out of sitemap urls.
* Added the new :class:`djpcms.plugins.defaults.SoftNavigation` plugin.
* Added :setting:`SITE_NAVIGATION_LEVELS` setting for controlling
  the number of nesting on the main site navigation.
  The site navigation is included in the template by
  using ``{{ sitenav.render }}``.
* Refactored :mod:`djpcms.utils.uniforms` so that :attr:`djpcms.utils.uniforms.FormLayout.default_style` is passed
  to the :func:`djpcms.utils.uniforms.UniFormElement.render` method.
* YUI-grid templates completed in ``djpcms/yui`` template directory.
* Refactoring in :mod:`djpcms.plugins`.
* **23 unit tests**.


Version 0.7.3 (2010-Sep-13)
==============================
* Re-registering a model to ``djpcms.views.appsite.site`` won't raise any error. It overrides the previous model application.
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
* **BACKWARD INCOMPATIBLE CHANGES**
* To use this version, changes needs to be made when importing ``djpcms`` modules.
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
* Added ``autocomplete`` and ``uniforms`` modules.
* ``ModelApplication`` and ``DJPplugin`` metaclasses derive from ``forms.MediaDefiningClass``.
* Added color picker jquery plugin from http://www.eyecon.ro/colorpicker/.
* When serving media files add applications media roots in `urls`.
* Added `list_display` a la django admin in `views.appsite` so that lists of objects can be displayed as a table.
* Added tablesorter jQuery plugin from http://tablesorter.com.
* Added `compress_if_you_can` template tag for compressing media files using third party libraries..
* Added `django-compressor` to contrib.
* Started decoupling from django. Still very much a django app right now.
* Compatible with django 1.2 and multidatabase.
* Bug in views.apps.flowrepo.appurl.FlowRepoApplication.has_permission fixed.
* TagArchiveView title overwritten.
* moved to jQuery 1.4.1.
* Added swfobject in media.
* added jstree from http://www.jstree.com/.
* Added jquery.pagination for pagination of search results.
* Introduced the pagecache object for caching Pages.
* Sitemap handled by pagecache. For now only static pages and application pages without arguments are included.
* Added lloogg_analytics and css_validators in template tags.
* NEW FIELD IN PAGE MODEL!! Added doctype field for specifying document type (HTML 4.01, XHTML 1, HTML 5).
* NEW FIELD IN PAGE MODEL!! Added insitemap for disabling a page from sidemap and robots.
* Refactored search form plugin - django form compatible template.
* Added autocomplete-off javascript decorator - so that xhtml validates.
* url resolver split between main urls and sub-applications.
* Better title in flowrepo contentview.

 
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
* Added jquery.cicle_ in ``media``, a javascript plugin to handle rotating pictures.
* Added plugin's url for handling dynamic plugins not connected to a model.
* Added Contact form plugin.
* ADDED NEW MODEL AdditionalPageData for injecting ad-hoc data into page head or javascript in page body
* Content text plugin is now wrapped into a div with class 'djpcms-text-content'.
* Breadcrumbs name is given by view title
* Created the DjpResponse object in views.response.

 
Version 0.4 (2009-Dec-24)
=========================================

* First official Alpha release.


.. _South: http://south.aeracode.org/
.. _stdnet: http://github.com/lsbardel/python-stdnet
.. _jquery.cicle: http://jquery.malsup.com/cycle/
.. _sphinx: http://sphinx.pocoo.org 