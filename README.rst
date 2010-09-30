
.. rubric:: Dynamic Content management System for Python and Javascript

--

:Web:
:Documentation: http://djpcms.com/docs/
:Dowloads: http://pypi.python.org/pypi/djpcms/
:Source: http://github.com/lsbardel/djpcms
:Keywords: web, cms, dynamic, ajax, django, jquery

--

Djpcms is a dynamic Content Management System which uses Python with django on the server side
and Javascript with jQuery on the browser side. It is designed to handle dynamic applications which require
high level of customization. Lots of AJAX enabled features including inline editing, autocomplete and
ajax forms.

.. _intro-features:

Features
===============================

 * Extendible using plugins.
 * Dynamic pages based on database models (not only django models).
 * Inline editing of plugins and pages.
 * Autocomplete for models when registered.
 * Extendible AJAX decorators.
 * Tagging with django-tagging_ (optional).
 * Several battery included application classes.
 * Integration of any Django app which provides ``urls.py``.
 * Nice form layout with extendible uniforms.
 * Deployment tools using fabric_.
 * South_ support for database migration.
 * Sitemap design.


.. _intro-installing:

Installing
================================
You can download the latest archive from pypi__, uncompress and::

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
It requires Python__ 2.5 or above. It is not yet compatible with Python 3 series.
Currently it depends on django_, however in the long run, this dependency will be
removed so that it can be used with other web-frameworks as well.

* django_.
* PIL_, the python image library.


Optional requirements:

 * django-tagging_ for tag management.
 * fabric_ and pip_ for the ``djpcms.contrib.jdep`` module.


__ http://pypi.python.org/pypi?:action=display&name=djpcms
__ http://www.python.org/
.. _django: http://www.djangoproject.com/
.. _django-tagging: http://code.google.com/p/django-tagging/
.. _PIL: http://www.pythonware.com/products/pil/
.. _fabric: http://docs.fabfile.org/
.. _pip: http://pip.openplans.org/
.. _South: http://south.aeracode.org/