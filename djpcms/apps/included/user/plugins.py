from djpcms.plugins import DJPplugin


class ObjectForUserList(DJPplugin):
    '''Display a list of model instances related
    to an authenticated user.'''
    def render(self, djp, wrapper, prefix, **kwargs):
        view = djp.view
        appmodel = getattr(view,'appmodel',None)
        if not appmodel:
            return ''
        request = djp.request
        user = request.user
        if not user.is_authenticated():
            return ''