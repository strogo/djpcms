
Extend ``djpcms`` user application with social authentication via ``AOuth``.


Usage
================
To use it simply add ``djpcms.contrib.social`` to your the ``INSTALLED_APPS``
Add yor token-secret pairs for the social ``providers`` in your settings file::

	SOCIAL_OAUTH_CONSUMERS = {'twitter':(twitter-key,twitter-seceret),
                          	  'google':('google-key','google-secret),
                          	  ...
                            }

Requirements
==================
* ``flickr``, requires flickrapi_
* ``google``, requires gdata_.
* ``twitter``, requires tweepy_.


.. _flickrapi: http://pypi.python.org/pypi/flickrapi
.. _gdata: http://code.google.com/p/gdata-python-client/
.. _tweepy: https://github.com/joshthecoder/tweepy
