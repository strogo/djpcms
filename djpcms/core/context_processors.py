import datetime
from djpcms import sites


def djpcms(request):
    settings = sites.settings
    ctx = {'jsdebug': 'true' if settings.DEBUG else 'false',
           'request': request,
           'debug': settings.DEBUG,
           'release': not settings.DEBUG,
           'now': datetime.datetime.now(),
           'MEDIA_URL': settings.MEDIA_URL,
           'site_admin_url': settings.ADMIN_URL_PREFIX,
           'login_url': settings.LOGIN_URL,
           'logout_url': settings.LOGOUT_URL}
    site = getattr(request,'site',None)
    if site:
        userapp = site.getapp('account')
        if userapp:
            userapp = userapp.appmodel
            if getattr(userapp,'userpage',False):
                url = userapp.viewurl(request, request.user)
            else:
                url = userapp.baseurl
            ctx.update({'user_url': url})
    return ctx
