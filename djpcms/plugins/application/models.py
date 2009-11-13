from django import forms
from django.db import models

from djpcms.utils import NoAjaxKeyError
from djpcms.models import DJPplugin, Page
from djpcms.djutils.fields import LazyChoiceField
from djpcms.html import formlet, submit
from djpcms.djutils import form_kwargs
from djpcms.forms import LazyChoiceField
from djpcms import functiongenerator, custom_response
    

        
class IntenalFunction(DJPplugin):
    application = models.CharField(max_length = 200, blank = True)
    arguments   = models.CharField(blank = True, max_length = 200, help_text = 'Comma separated list of arguments for the applications') 
    
    def __unicode__(self):
        b = super(IntenalFunction,self).__unicode__()
        return u'%s: %s' % (b,self.application or '')
    
    def get_arguments(self):
        if self.arguments:
            return tuple(self.arguments.replace(' ','').split(','))
        else:
            return ()
    
    def render(self, cl, prefix, wrapper):
        attr = custom_response(self.application)
        if attr:
            args = self.get_arguments()
            return attr(cl,*args)
        else:
            return u''
    
    def changeform(self, request = None, prefix = None):
        return IntenalFunctionForm(**form_kwargs(request, instance = self, prefix = prefix))    
    
    

class DynamicApplication(DJPplugin):
    '''
    Plugin for general Django applications.
    @param app_page: a Page instance to provide the functionality. Note this page must have the app_type field not empty
    @param title: Just the title to display in the widget
    @param arguments: IMPORTANT, to have more granularity on applications, some arguments can be specified  
    '''
    application = models.CharField(max_length = 200, blank = True)
    arguments   = models.CharField(blank = True, max_length = 200, help_text = 'Comma separated list of arguments for the applications') 
    
    def __unicode__(self):
        b = super(DynamicApplication,self).__unicode__()
        return u'%s: %s' % (b,self.application or '')
    
    def get_arguments(self):
        if self.arguments:
            args = self.arguments.replace(' ','').split(',')
            nargs  = []
            kwargs = {}
            for a in args:
                ca = a.split('=')
                if len(ca) == 2:
                    kwargs[str(ca[0])] = ca[1]
                else:
                    nargs.append(a)
            return tuple(nargs),kwargs
        else:
            return (),{}
        
    def get_appview(self, view):
        from djpcms.plugins.application import appsite
        try:
            return appsite.site.getapp(self.application)
        except:
            return view
        
    def render(self, cl, prefix, wrapper):
        '''
        Rendering the dynamic application
        @param request: HttpRequest instance
        @param prefix: string to use as prefix in forms
        @param wrapper: instance of djpcms.plugins.wrapper.ContentWrapperHandler used for layout informations
        @param view: instance of djpcmsview 
        '''
        from django.conf import settings
        if not self.application:
            return u''
        try:
            app = self.get_appview(cl.view)
            if app:
                # get url arguments if provided
                args, kwargs = self.get_arguments()
                return app.render(cl.request, prefix, wrapper, *args, **kwargs)
            else:
                if settings.DEBUG:
                    return u'Could not find application %s' % self.application
                else:
                    return u''
        except Exception, e:
            if settings.DEBUG:
                return u'%s' % e
            else:
                raise e
        
    def changeform(self, request = None, prefix = None):
        from djpcms.plugins.application import appsite
        return appsite.ChangeForm(**form_kwargs(request, instance = self, prefix = prefix))    


class IntenalFunctionForm(forms.ModelForm):
    application = LazyChoiceField(choices = functiongenerator)
    
    class Meta:
        model = IntenalFunction
        
        
