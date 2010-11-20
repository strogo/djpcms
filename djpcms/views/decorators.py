from djpcms.views import appview


def deleteview(f, **kwargs):
    class _(appview.DeleteView):
        def default_post(self, djp):
            return appview.deleteinstance(djp,f)
    _.__name__ = '%s_DeleteView' % f.__name__
    return _(**kwargs)