from conf import *

ADMINS = (
     ('Luca Sbardella', 'luca.sbardella@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(basedir,'sitedjpcms.sqlite'),
    }
}