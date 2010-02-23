import datetime
from django.conf import settings
from djpcms.settings import HTML_CLASSES

def djpcms(request):
    now = datetime.datetime.now()
    djdeb = 'false'
    if settings.DEBUG:
        djdeb = 'true'
    return {'jsdebug': djdeb,
            'debug': settings.DEBUG,
            'release': not settings.DEBUG,
            'now': now,
            'site_admin_url': settings.ADMIN_URL_PREFIX,
            'login_url': settings.LOGIN_URL,
            'logout_url': settings.LOGOUT_URL}