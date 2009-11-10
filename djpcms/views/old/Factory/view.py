from copy import deepcopy

from django.utils.datastructures import SortedDict
from django.http import Http404

from djpcms.views import cache
from djpcms.views.base import baseview
from djpcms.utils import urlbits

from fchild import child


__all__ = ['view']


def get_declared_children(bases, attrs):
    """
    Create a list of factory view children instances from the passed in 'attrs',
    plus any similar fields on the base classes (in 'bases').
    This is used by the FactoryViewMetaClass.
    """
    children = []
    for child_name, obj in attrs.items():
        if isinstance(obj, child):
            attrs.pop(child_name)
            obj.code = child_name
            children.append((child_name,obj)) 
    
    #children = [(child_name, attrs.pop(child_name)) for child_name, obj in attrs.items() if isinstance(obj, child)]
    children.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))

    # If this class is subclassing another Factory,
    # add that Factory's children.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    for base in bases[::-1]:
        if hasattr(base, 'base_children'):
            children = base.base_children.items() + children

    return SortedDict(children)


class FactoryViewMetaClass(type):
    
    def __new__(cls, name, bases, attrs):
        attrs['base_children'] = get_declared_children(bases, attrs)
        return super(FactoryViewMetaClass, cls).__new__(cls, name, bases, attrs)
    


class FactoryViewBase(baseview):
    default_view = 'search'
    '''
    A factory view can handle several subviews
    according to its internal pagination.
    The subview have a handle on the factory view.
    This class overwrite the response method of baseview.
    '''
    def __init__(self, *args, **kwargs):
        self.children = deepcopy(self.base_children)
        
    def get_child(self, args):
        '''
        args must be a list
        '''
        subview = args.pop(0)
        cview   =  self.children.get(subview,None)
        if cview:
            return cview.get(self, args)
        else:
            return None
        
    def isfactory(self):
        return True
    
    def set_default_handler(self, view):
        self.default_handler = view
        self._children.append(view)
        
    def response(self, request):
        return self.default_handler.response(request)
        
    def get_page_nav(self, request):
        papp = super(FactoryViewBase,self).get_page_nav(request)
        pnav = self.default_handler.get_page_nav(request)
        pnav.extend(papp)
        return pnav
    
    def newchildview(self, request, view = None, *args):
        '''
        Get a new child view
            @param request:    django request object
            @param view:       string or None indicating the child code
            @param args:       optional parameters for url composition
        '''
        if len(args) == 1:
            obj = args[0]
            if isinstance(obj,self.model):
                largs = urlbits(self.object_url(obj))
            else:
                largs = [obj]
        else:
            largs = list(args)
        largs.insert(0, view or self.default_view)
        return cache.childview(request, self, largs)
        
        

class view(FactoryViewBase):
    __metaclass__ = FactoryViewMetaClass


        
