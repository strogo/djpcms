from django import http
from djpcms.views.baseview import djpcmsview
from djpcms.plugins.application import appsite

_app_classes_dictionary = {}

class AppMetaClass(type):
    
     def __new__(cls, name, bases, attrs):
        global _app_classes_dictionary
        new_class = super(AppMetaClass, cls).__new__(cls, name, bases, attrs)
        
        found = False
        for base in bases:
            if base.__name__ == "appbase":
                found = True
                break
        if found:
            name = new_class.__name__
            new_class._applications = _app_classes_dictionary
            new_class.code          = name
            _app_classes_dictionary[name] = new_class
             
        return new_class
    


def modelpageselect(view, request):
    '''
    Select view for a application model
    '''
    page      = view.page
    model     = view.model
    modelsite = appsite.site.for_model(model)
    
    if not modelsite:
        raise http.Http404('model %s not in applications' % model)
    
    #TODO
    #Clean arguments for previous pages.
    #For now we assume that parent pages do not have arguments
    args = view.args
    ###########################################################
    
    # Get the application type
    app_type = page.app_type
    if not app_type:
        if not args:
            app_type = 'search'
        else:
            app_type = args.pop(0)
            
    handler = modelsite.getapp(app_type)
    if not handler:
        raise http.Http404('Application %s for model %s not available' % (app_type,model))
    
    view.args = args
    view.handler = handler
    

def get(name):
    global _app_classes_dictionary
    return _app_classes_dictionary.get(name,None)
    



def create_view(obj, appmodel):
    '''
    view object constructor
        @param dbmodel: the database model for the Page
        @param args:    list of arguments
        @param output_args:   a list or None
        @param edit:    string (Optional)
    '''
    obj.appmodel      = appmodel
    obj.editurl       = None
    obj._children     = {}
    obj.model         = appmodel.model
    obj.instance      = None
    obj.url           = None               
    return obj


class appdefault(djpcmsview):
    required_object  = False
    
    def __new__(cls, appmodel):
        return create_view(super(appdefault, cls).__new__(cls), appmodel)
    
    def get_url(self, request, *args):
        '''
        Calculate url
        '''
        # If the model has a page object obtain url from it:
        page = self.appmodel.get_page()
            
            
            
    def render(self, request, prefix, wrapper):
        pass
        
        
        
    
    
class appbase(appdefault):
    __metaclass__ = AppMetaClass


class add(appbase):
    '''
    Add application view
    '''
    def render(self, request, prefix, wrapper, *args):
        url = self.get_url(request, *args)
        return self.appmodel.get_form(request, self.instance, prefix, wrapper)
        

class edit(add):
    required_object = True

class delete(appbase):
    required_object = True

class search(appbase):
    pass