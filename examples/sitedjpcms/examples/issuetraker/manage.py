import djpcms
from stdnet import orm

site = djpcms.MakeSite(__file__,
                       CMS_ORM = 'stdnet',
                       APPLICATION_URL_MODULE = 'issuetraker.application',
                       USER_MODEL = 'issuetraker.models.User',
                       #HTTP_LIBRARY = 'werkzeug',
                       HTTP_LIBRARY = 'django',
                       INSTALLED_APPS = ('djpcms',
                                         'issuetraker',
                                         'stdnet.contrib.sessions'),
                       MIDDLEWARE_CLASSES = ('djpcms.middleware.CreateRootPage',
                                             'stdnet.contrib.sessions.middleware.SessionMiddleware',),
                       DEBUG = True,
                       )


orm.register_applications(site.settings.INSTALLED_APPS)

djpcms.serve(site)


