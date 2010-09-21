
Django module for managing deployment of applications using fabric_, virtualenv_ and pip_.

Currently the only server configuration available is nginx_ + apache with mod_wsgi_.

**It works on linux servers, no idea about windows.**


Requirements
=========================

On the developer machine

* fabric_
* pip_


On the server side

* virtualenv_
* pip_

 
Usage
==================
An example on how to use the package is in the ``examples\djpcms-site`` directory.
The directory structure of your site, which we call ``greatsite`` looks like this::

	greatsite-project/
	  greatsite/
	  __init__.py
	  requirements.txt
	  fabfile.py
	  
The ``fabfile.py`` is needed by fabric_ and should, at least, contain::

    from djpcms.contrib.jdep.fabtool import *
    utils.project('greatsite','greatsite.com')
        
The ``requirement.txt`` is needed by pip_ to install your site required pacakges.

Then run::

	fab --list
	
and you will have a list of possible commands. Type::

	fab -H your.host.com deploy
	
to deploy your site.


.. _fabric: http://docs.fabfile.org/
.. _virtualenv: http://virtualenv.openplans.org/
.. _pip: http://pip.openplans.org/
.. _nginx: http://nginx.org/
.. _mod_wsgi: http://code.google.com/p/modwsgi/
