
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
On the root directory of your django project create a file called ``fabfile.py`` which contains::

    from djpcms.contrib.jdep.fabtool import *
    utils.project('myproject','myproject.com')
        

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
