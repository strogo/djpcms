JDEP
===================

Django module for managing deployment of applications using fabric, virtualenv and pip.
The favorite configuration is djago served by Apache using `mod_wsgi`.


Requirements
=========================
 * fabric
 * pip
 * djpcms
 
On the server side
 * virtualenv
 * pip

 
Usage
==================
On the root directory of your django project create a file called `fabfile.py` which starts as::

    from django.core.management import setup_environ
    from myproject import settings
    setup_environ(settings)
    from djpcms.contrib.jdep.fabtool import *
    
    
    def winserver():
        "Use the production virtual server"
        context['server_type'] = 'w'