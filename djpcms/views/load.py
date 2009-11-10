from django.http import Http404

from djpcms.settings import GRID960_DEFAULT_FIXED


class DjpCmsViewError(Exception):
    pass


def handle_new_view(page, args, **kwargs):
    '''
    Create a new view object given a page model instance
    @param page: page instance
    @param args: list of arguments   
    '''
    view = page.object(args, **kwargs)
    
    # Check Factory options.
    if view.isfactory():
        if not hasattr(view,'default_handler'):
            default_handler = handle_new_view_from_view(view, [view.default_view])
            view.set_default_handler(default_handler)
        if not args:
            return view
        else:
            while args:
                view = handle_new_view_from_view(view, args)
    
    if args:
        raise Http404
    
    return view
