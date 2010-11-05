import datetime
from djpcms.conf import settings

def djpcms(request):
    return {'jsdebug': 'true' if settings.DEBUG else 'false',
            'request': request,
            'debug': settings.DEBUG,
            'release': not settings.DEBUG,
            'now': datetime.datetime.now(),
            'MEDIA_URL': settings.MEDIA_URL,
            'site_admin_url': settings.ADMIN_URL_PREFIX,
            'login_url': settings.LOGIN_URL,
            'logout_url': settings.LOGOUT_URL}