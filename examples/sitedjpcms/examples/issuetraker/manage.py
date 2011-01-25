'''
Script for running the IssueTracker application as stand-alone
'''
import djpcms
from stdnet import orm


def appurls():
    from djpcms import sites
    from djpcms.apps.included import user, static
    from stdnet.contrib.sessions.models import User
    from .application import IssueTraker, Issue
    
    return (
            static.Static(sites.settings.MEDIA_URL, show_indexes=True),
            user.UserApplication('/accounts/', User),
            IssueTraker('/',Issue),
            )


if __name__ == '__main__':
    site = djpcms.MakeSite(__file__,
                           CMS_ORM = 'stdnet',
                           APPLICATION_URL_MODULE = 'issuetraker.manage',
                           USER_MODEL = 'issuetraker.models.User',
                           #HTTP_LIBRARY = 'werkzeug',
                           HTTP_LIBRARY = 'django',
                           INSTALLED_APPS = ('djpcms',
                                             'issuetraker',
                                             'stdnet.contrib.sessions'),
                           MIDDLEWARE_CLASSES = ('djpcms.middleware.CreateRootPageAndUser',
                                                 'stdnet.contrib.sessions.middleware.SessionMiddleware',),
                           DEBUG = True,
                       )
    orm.register_applications(site.settings.INSTALLED_APPS)
    djpcms.serve(site)


