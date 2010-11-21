
Django module for managing deployment of applications using fabric_, virtualenv_ and pip_.

Currently the only server configuration available is nginx_ + apache with mod_wsgi_.

**It works on linux servers**


.. contents::
    :local:


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
	  certificates/
	  __init__.py
	  requirements.txt
	  fabfile.py
	  
The ``fabfile.py`` is needed by fabric_ and should, at least, contain::

    from djpcms.contrib.jdep.fabtool import *
    utils.project('greatsite','greatsite.com', **kwargs)
        
where ``kwargs`` is a dictionary containing the deployment :ref:`parameters <parameters>`.
The ``requirement.txt`` is needed by pip_ to install your site required packages.
The ``certificates`` directory is optional and can be used to upload ``SSL`` certificate and ``key``.

Then run::

	fab --list
	
and you will have a list of possible commands.


deploy
--------------
This is command does deployment of your site into the production server. Just type::

	fab -H your.host.com deploy
	

info
---------------
Display all :ref:`parameters <parameters>` used for deployment::

	fab info

serverconfig
-----------------
Create server configuration files on local directory as specified by the ```server_type`` parameter::

	fab serverconfig

This is useful for testing/development purposes when running your site locally. 

.. _parameters:

Parameters
========================
* ``deploy_root_dir`` The deployment root directory. Default ``deployment``.
  This directory will be created, if it does not exist, on the home directory of the user installing on the remote machine.
  In other words if the user is ``siteuser``, the deployment root directory will be ``/home/siteuser/deployment`` if
  the home directory of ``siteuser`` is ``/home/siteuser/``.
* ``redirects`` List of urls which will be redirected to your site home page. Default ``[]``.
* ``redirect_port`` port number to redirect requests handled by ``djpcms``. Default ``90``.
* ``secure`` boolean indicating if connection is over ``https``. Default ``False``.
* ``server_port`` server port. Default ``80`` i ``secure`` is ``False`` else ``443``.
* ``server_type`` string indicating the server configuration. Available
	* ``nginx-twisted`` for twisted web behind bginx.
	* ``nginx-apache-mod_wsgi`` for apache mod_wsgi behind nginx.
 Default: ``nginx-apache-mod_wsgi``.
* ``setting_module`` the django settings module name. Default ``settings``.

After deploy hook
========================
There is the possibility of registering function to call once the deployment has been performed. To
register a function, your ``fabfile.py`` could be::

	from djpcms.contrib.jdep.fabtool import *
    utils.project('greatsite','greatsite.com')
    
    def myhook1():
    	#do some clever stuff here
    	return
    
    utils.after_deploy_hook.append(myhook1)

	


.. _fabric: http://docs.fabfile.org/
.. _virtualenv: http://virtualenv.openplans.org/
.. _pip: http://pip.openplans.org/
.. _nginx: http://nginx.org/
.. _mod_wsgi: http://code.google.com/p/modwsgi/
