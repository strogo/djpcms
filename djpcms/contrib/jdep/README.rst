
Django module for managing deployment of applications using fabric_, virtualenv_ and pip_.
The favorite configuration is django served by Apache using `mod_wsgi`.

**Only Ubuntu server supported for now**


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
On the root directory of your django project create a file called `fabfile.py` which starts as::

    from djpcms.contrib.jdep.fabtool import *
    utils.project('myproject')
        
        
Then run::

	fab deploy


.. _fabric: http://docs.fabfile.org/
.. _virtualenv: http://virtualenv.openplans.org/
.. _pip: http://pip.openplans.org/
