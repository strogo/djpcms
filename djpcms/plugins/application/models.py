from django import forms
from django.db import models

from djpcms.utils import json
from djpcms.utils import NoAjaxKeyError
from djpcms.models import DJPplugin, Page
from djpcms.djutils.fields import LazyChoiceField
from djpcms.html import formlet, submit
from djpcms.djutils import form_kwargs
from djpcms.forms import LazyChoiceField
from djpcms import functiongenerator, custom_response
    
    
    
def get_arguments(arguments):
    '''
    Only keyworded arguments are allowed
    '''
    if arguments:
        try:
            d = json.loads(arguments)
            if isinstance(d,dict):
                return d
        except:
            pass

        
class IntenalFunction(DJPplugin):
    '''
    Internal Function plugin
    '''
    application = models.CharField(max_length = 200, blank = True)
    arguments   = models.CharField(blank = True, max_length = 200) 
    
    def __unicode__(self):
        b = super(IntenalFunction,self).__unicode__()
        return u'%s: %s' % (b,self.application or '')
    
    def render(self, djp):
        attr = custom_response(self.application)
        if attr:
            kwargs = get_arguments(self.arguments)
            if kwargs:
                djp.update(**kwargs)
            return attr(djp)
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
        
    def render(self, djp):
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
            app = self.get_appview(djp.view)
            if app:
                kwargs = get_arguments(self.arguments)
                if kwargs:
                    djp.update(**kwargs)
                return app.render(djp)
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
        
        
