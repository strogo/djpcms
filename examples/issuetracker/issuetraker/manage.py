import djpcms

djpcms.MakeSite(__file__,
                'conf',
                CMS_ORM = 'stdnet',
                APPLICATION_URL_MODULE = 'issuetraker.application',
                USER_MODEL = 'issuetraker.models.User',
                INSTALLED_APPLICATIONS = ('djpcms',
                                          'issuetraker')
                )

djpcms.serve()


