
.. rubric:: Plugins-based content management System for
    dynamic applications written in Python and Javascript

--

:Web: http://djpcms.com/
:Documentation: http://djpcms.com/docs/
:Dowloads: http://pypi.python.org/pypi/djpcms/
:Source: http://github.com/lsbardel/djpcms
:Keywords: web, cms, dynamic, ajax, django, jquery

--

Djpcms is a dynamic Content Management System which uses Python with django_ on the server side
and Javascript with jQuery_ on the browser side. It is designed to handle dynamic applications which require
high level of customization. Lots of AJAX enabled features including inline editing, autocomplete and
ajax forms.

It is based on django, but it works for other object relational mappers too!

.. _intro-features:

Features
===============================

 * Dynamic pages based on database models, not only django_ models!
 * If you need more than django_ and stdnet_ models,
   register your model type and off you go::
 
 	from djpcms.core.models import ModelTypeWrapper, register
 	
 	class MyModelType(ModelTypeWrapper):
 	
 	    def setup(self):
 	        '''Set up your model type for djpcms interaction'''
 	   
 	    def test(self, model):
 	        '''test if model is a type handled by this wrapper'''  
 	
 	register('mymodeltype',MyModelType)
 	
 	
 * Extendible using plugins::
 
 	from djpcms.plugins import DJPplugin
 	
 	class MyPlugin(DJPplugin):
 	
 	    def render(self, djp, **kwargs):
 	        ...
 	        
 * Inline editing of plugins and pages.
 * Autocomplete for models when the autocomplete view is added to the model application.
 * Extendible AJAX decorators.
 * Tagging with django-tagging_ (optional).
 * Several battery included application classes.
 * Integration of any Django app which provides ``urls.py``.
 * Nice form layout with extendible ``uniforms``.
 * Deployment tools using fabric_.
 * South_ support for database migration.
 * Sitemap design.


.. _intro-installing:

Installing
================================
You can download the latest archive from pypi_, uncompress and::

	python setup.py install
	
Otherwise you can use pip::

	pip install djpcms
	
or easy_install::

	easy_install djpcms
	


Running tests
===================

On the top level directory type::

	python runtests.py
	
Otherwise, once installed::

	import djpcms
	djpcms.runtests()


Dependencies
========================
It requires Python_ 2.6 or above. It is not yet compatible with Python 3 series.
Currently it depends on django_, however in the long run, this dependency will be
removed so that it can be used with other web-frameworks as well.

* django_.
* PIL_, the python image library.


Optional requirements:

* django-tagging_ for tag management.
* fabric_ and pip_ for the ``djpcms.contrib.jdep`` module.


Kudos
=====================
Djpcms includes several open-source libraries and plugins developed by other authors:

* jQuery_ the building block of the browser side of djpcms.
  Thanks to the jQuery and jQuery-UI teams!
  The latest jquery and jquery-ui minified files are shipped the library. 
* jQuery tablesorter_ plugin. Thanks to Christian Bach.
* Modernizr_, a small JavaScript library that detects the availability of native implementations for next-generation web technologies.

.. _pypi: http://pypi.python.org/pypi?:action=display&name=djpcms
.. _Python: http://www.python.org/
.. _django: http://www.djangoproject.com/
.. _jQuery: http://jquery.com/
.. _django-tagging: http://code.google.com/p/django-tagging/
.. _PIL: http://www.pythonware.com/products/pil/
.. _fabric: http://docs.fabfile.org/
.. _pip: http://pip.openplans.org/
.. _South: http://south.aeracode.org/
.. _stdnet: http://code.google.com/p/python-stdnet/
.. _tablesorter: http://tablesorter.com/
.. _Modernizr: http://www.modernizr.com/

