import os
from djpcms._settings import configure, DJPCMS_ENVIRONMENT_VARIABLE
FRAMEWORK = os.environ.get(DJPCMS_ENVIRONMENT_VARIABLE,'django')

if FRAMEWORK == 'django':
    from django.conf import settings
else:
    raise NotImplementedError('At the moment only django framework is supported')

configure(settings)