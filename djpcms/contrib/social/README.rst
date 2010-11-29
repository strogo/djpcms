
Extend ``djpcms`` user application with social authentication via ``AOuth``.


Usage
================
To use it simply add ``djpcms.contrib.social`` to your the ``INSTALLED_APPS`` and
add your token-secret pairs for the social ``providers`` you want in your settings file::

	SOCIAL_OAUTH_CONSUMERS = {'twitter':(twitter-key,twitter-seceret),
                          	  'google':('google-key','google-secret),
                          	  ...
                            }
                            
If you want your application to create users, set the flag::

	SOCIAL_AUTH_CREATE_USERS = True
	

Requirements
==================
* httplib2_ no other ``http`` python library is better than this one.
* python-oauth_
* ``flickr``, requires flickrapi_
* ``google``, requires gdata_.
* ``twitter``, requires tweepy_.


.. _httplib2: http://code.google.com/p/httplib2/
.. _python-oath: https://github.com/leah/python-oauth
.. _flickrapi: http://pypi.python.org/pypi/flickrapi
.. _gdata: http://code.google.com/p/gdata-python-client/
.. _tweepy: https://github.com/joshthecoder/tweepy
