
.. rubric:: Plugins-based content management System for
    dynamic applications written in Python and Javascript

--

:Web: http://djpcms.com/
:Documentation: http://djpcms.com/docs/
:Dowloads: http://pypi.python.org/pypi/djpcms/
:Source: http://github.com/lsbardel/djpcms
:Keywords: web, cms, dynamic, ajax, python, jquery

--

Djpcms is a dynamic Content Management System which uses Python with django_ on the server side
and Javascript with jQuery_ on the browser side. It is designed to handle dynamic applications which require
high level of customization. Lots of AJAX enabled features including inline editing, autocomplete and
ajax forms.

It is based on django models, for now, but it will work for other object relational mappers too!

.. contents::
    :local:

.. _intro-features:

Features
===============================

 * Dynamic pages based on database models.
 * Applications based on database model or not.
 * Extendible using ``plugins``.
 * Inline editing of ``plugins`` and ``pages``.
 * Move ``plugins`` in page using drag-and-drop functionalities.
 * ``Autocomplete`` for models when the autocomplete view is added to the model application.
 * Extendible AJAX decorators.
 * Tagging with django-tagging_, included in distribution.
 * Several battery included application classes.
 * Integration with ``Django`` and South_ support for database migration.
 * Nice form layout with extendible ``uniforms``.
 * Deployment tools using fabric_.
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
	
	
Version Check
=====================

To check the version::

	>>> import djpcms
	>>> djpcms.__version__
	'0.8.5'
	>>> djpcms.get_version()
	'0.8.5'
	
	
Running tests
===================

On the top level directory type::

	python runtests.py
	
For options in running tests type::

    python runtests.py --help
	
To access coverage of tests you need to install the coverage_ package and run the tests using::

	coverage run runtests.py
	
and to check out the coverage report::

	coverage report -m
	

Dependencies and Python 3
===========================
It requires Python_ 2.6 or above. It is not yet compatible with Python 3 series but
it will be ported as soon as the library is independent from django_ and the API is stable enough.
As mentioned it idepends on django_, however in the long run, this dependency will be
removed so that it can be used with other web-frameworks as well.

* django_.
* PIL_, the python image library.


Optional requirements:

* fabric_ and pip_ for the ``djpcms.contrib.jdep`` module.


Kudos
=====================
Djpcms includes several open-source libraries and plugins developed
by other authors and communities:

Python
---------
* django-tagging_ for tag management. Shipped with the library in the ``libs`` module but a library in its own.

JavaScript
------------
* jQuery_ core and UI are the building block of the browser side of djpcms. 
* jQuery tablesorter_ plugin for managing dynamic tables.
* jQuery jstree_ plugin for managing tree components. 
* jQuery cycle_ plugin for photo galleries. 
* jQuery Sparklines_ plugin for inline plotting.
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
.. _jstree: http://www.jstree.com/
.. _cycle: http://jquery.malsup.com/cycle/
.. _Sparklines: http://www.omnipotent.net/jquery.sparkline/
.. _coverage: http://nedbatchelder.com/code/coverage/
