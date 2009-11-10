import copy

from django.http import Http404, HttpResponseRedirect

from djpcms.settings import GRID960_DEFAULT_FIXED
from djpcms.views.base import baseview
from djpcms.utils import setlazyattr
from djpcms.db.interfaces import getobject


class child(object):
    '''
    child is a factory class used to generate child views
    '''
    creation_counter = 0
    
    def __init__(self,
                 display = None,
                 view    = None,
                 robj    = False,
                 in_nav  = True,
                 template_name = None,
                *args, **kwargs):
        '''
        display  Text to display as link.
        view     a childview class (not instance)
        robj     if True a model instance is required by the view
        in_nav   Whether the view is visible in navigation
        '''
        self.__code        = None
        self.view          = view
        self.display       = display
        self.requireobject = robj
        self.in_nav        = in_nav
        self.template_name = template_name
        self.grid_fixed = kwargs.pop('grid_fixed',None)
        # Increase the creation counter, and save our local copy.
        self.creation_counter = child.creation_counter
        child.creation_counter += 1
    
    def __get_code(self):
        return self.__code
    def __set_code(self, code):
        self.__code  = code
        self.display = self.display or code
    code = property(fget = __get_code, fset = __set_code)
    
    def __unicode__(self):
        return u'%s - %s' % (self.code,self.display)
    
    def __str__(self):
        return str(self.__unicode__())
    
    def get(self, factory, args, **kwargs):
        '''
        Create a child view object
        '''
        gf = self.grid_fixed
        if gf is None:
            gf = factory.grid_fixed
        return self.view(factory.page, args, child = self, factory = factory, grid_fixed = gf, **kwargs)
        
    def __deepcopy__(self, memo):
        result = copy.copy(self)
        memo[id(self)] = result
        return result



class childview(baseview):
    '''
    Base class for Factory child views
    '''
    def processargs(self, args):
        '''
        Process arguments tuple.
        Arguments are string or model objects used to calculate the url.
        '''
        self.parentview = self.factory
        oargs = args[:]
        N = len(args)
        for i in range(0,N):
            args.pop()
        rargs = oargs[:]
        self.get_object(oargs)
        if self._child.requireobject and not self.object:
            raise Http404
        return rargs
        
    def make_url(self, args):
        url = '%s%s/' % (self.factory.url, self._child.code)
        if args:
            url = '%s%s/' % (url,'/'.join(args))
        return url
    
    def get_object(self, args):
        '''
        @param args: list or url bits
        @return: a list of url bits used to create the object url
         
        This function is the only one to override.
        it create the object and/or handle extra arguments.
        IMPORTANT
        args should changed during the function call so that what is left is
        used by a subsequent function called.
        '''
        if args:
            code = args[0]
            self.object = getobject(self.model,code)
        
    def get_page_nav(self, request):
        views = self.factory.children
        c     = self._child
        vv = []
        for code,sb in views.items():
            if c == sb:
                continue
            
            if sb.in_nav:
                if not c.requireobject and sb.requireobject:
                    continue
                else:
                    if sb.requireobject:
                        view = self.factory.newchildview(request,code,self.object)
                    else:
                        view = self.factory.newchildview(request,code)
                    if view:
                        vv.append(view)
        return vv
    
    def appendself(self):
        return self.factory
    
    def urldisplay(self):
        return self._child.display
    
    def newchildview(self, request, view = None, *args, **kwargs):
        '''
        Retrive a new child view from the factory.
         If view is not defined the default view is returned
         view String or None
        '''
        return self.factory.newchildview(request, view,*args)
    
    def editview(self, request = None, obj = None):
        '''
        shortcut for edit view. Can be reimplemented
        '''
        return self.newchildview(request, 'edit', obj or self.object)
    
    def addview(self, request):
        '''
        shortcut for add view. Can be reimplemented
        '''
        return self.newchildview(request, 'add')
    
    def viewview(self, request = None, obj = None):
        '''
        shortcut for view view. Can be reimplemented
        '''
        return self.newchildview(request, 'view', obj or self.object)
    
    def deleteview(self, request = None, obj = None):
        '''
        shortcut for view view. Can be reimplemented
        '''
        return self.newchildview(request, 'delete', obj or self.object)
        
    def factoryurl(self, request, view = None, *args, **kwargs):
        '''
        Retrive a url within the factory view.
          view is a string representing a particular subview (ad, edit, search, etc...)   
        '''
        sb = self.newchildview(request, view, *args, **kwargs)
        if sb:
            return sb.url
        else:
            return None
        
    def childurlbase(self, view = None):
        if view == None:
            view = self._child.code
        sb = self.factory.children.get(view, None)
        if sb:
            return '%s%s/' % (self.factory.url,sb.code)
        else:
            return None
    
    def redirect_to(self, url = None):
        if url == None:
            url = self.factory.url
        return HttpResponseRedirect(url)

    
class objectdeleteview(childview):
    authflag    = 'delete'
    
    #TODO, a get view should not change anything,
    # here we are deleting an object!!!!!!
    # to sort out
    def view_contents(self, request, params):
        self.object.delete()
        return self.redirect_to()

