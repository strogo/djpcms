
Extend ``djpcms`` user application with social authentication via ``AOuth``.


Usage
================
To use it simply add ``djpcms.contrib.social`` to your the ``INSTALLED_APPS`` and
add your token-secret pairs for the social ``providers`` you want in your settings file::

	SOCIAL_OAUTH_CONSUMERS = {'twitter':(twitter-key,twitter-seceret),
                          	  'google':('google-key','google-secret),
                          	  ...
                            }

Requirements
==================
* httplib2_ no other ``http`` python library is better than this one.
* ``flickr``, requires flickrapi_
* ``google``, requires gdata_.
* ``twitter``, requires tweepy_.


.. _httplib2: http://code.google.com/p/httplib2/
.. _flickrapi: http://pypi.python.org/pypi/flickrapi
.. _gdata: http://code.google.com/p/gdata-python-client/
.. _tweepy: https://github.com/joshthecoder/tweepy
