from datetime import datetime

from django import http
from django.utils.dateformat import format
from django.utils.translation import ugettext_lazy as _

from djpcms.utils.html import submit
from djpcms.utils import force_unicode
from djpcms.utils.ajax import jredirect



def form_kwargs(request,
                instance = None,
                withrequest = False,
                withdata = True,
                method = 'POST',
                own_view = True,
                inputs = None,
                **kwargs):
    '''Form arguments aggregator.
Usage::

    form = MyForm(**form_kwargs(request))

'''
    if request and withdata and request.method == method and own_view:
        data = getattr(request,method)
        if inputs:
            bind = False
            for input in inputs:
                if input._attrs['name'] in data:
                    bind = True
        else:
            bind = True
        if bind:
            kwargs['data'] = data
            kwargs['files'] = request.FILES
    if withrequest:
        kwargs['request'] = request
    if instance:
        kwargs['instance'] = instance
    return kwargs


def add_extra_fields(form, name, field):
    '''form must be a form class, not an object
    '''
    fields = form.base_fields
    if name not in fields:
        fields[name] = field
    meta = getattr(form,'_meta',None)
    if meta:
        fields = meta.fields
        if fields and name not in fields:
            fields.append(name)
    return form


def add_hidden_field(form, name, required = False):
    from django import forms
    return add_extra_fields(form,name,forms.CharField(widget=forms.HiddenInput, required = required))


def success_message(instance, mch):
    from djpcms.conf import settings
    dt = datetime.now()
    c = {'dt': format(dt,settings.DATETIME_FORMAT),
         'mch': mch,
         'obj': instance}
    if instance:
        c['name'] = force_unicode(instance._meta.verbose_name)
        return _('The %(name)s "%(obj)s" was succesfully %(mch)s %(dt)s') % c
    else:
        return _('%(mch)s %(dt)s') % c


def update_initial(request, form_class, initial = None, own_view = True):
    if request.method == 'GET':
        params = dict(request.GET.items())
        next   = params.get('next',None)
        _current_url = request.path
        if not next and not own_view:
            next = _current_url
        if next:
            form_class = add_hidden_field(form_class,'next')
        form_class = add_hidden_field(form_class,'_current_url')
        initial = initial or {}
        initial['next'] = next
        initial['_current_url'] = _current_url
    return initial


def get_form(djp,
             form_class,
             method = 'POST',
             initial = None,
             prefix = None,
             wrapped = True,
             form = None,
             addinputs = None,
             withdata = True,
             instance  = None,
             model = None,
             form_withrequest = None,
             template = None,
             form_ajax = False,
             withinputs = False):
    '''Build a form:
    
* *djp*: instance of djpcms.views.DjpRequestWrap.
* *initial*: If not none, a dictionary of initial values for model fields.
* *prefix*: prefix to use in the form.
* *wrapper*: instance of djpcms.plugins.wrapper.ContentWrapperHandler with information on layout.
'''
    from djpcms.utils.uniforms import UniForm
    request  = djp.request
    own_view = djp.own_view()
    
    initial = update_initial(request, form_class, initial, own_view = own_view)
    
    inputs = getattr(form_class,'submits',None)
    if inputs:
        inputs = [submit(value = val, name = nam) for val,nam in inputs]
    elif addinputs:
        inputs = addinputs(instance, own_view)
            
    f     = form_class(**form_kwargs(request     = request,
                                     initial     = initial,
                                     instance    = instance,
                                     prefix      = prefix,
                                     withdata    = withdata,
                                     withrequest = form_withrequest,
                                     method      = method,
                                     own_view    = own_view,
                                     inputs      = inputs if withinputs else None))
        
    wrap = UniForm(f,
                   request  = request,
                   instance = instance,
                   action   = djp.url,
                   inputs   = inputs,
                   template = template)
    if form_ajax:
        wrap.addClass(djp.css.ajax)
    wrap.is_ajax = request.is_ajax()
    if model:
        wrap.addClass(str(model._meta).replace('.','-'))
    return wrap

    
def saveform(djp, editing = False):
    '''Comprehensive save method for forms'''
    view       = djp.view
    request    = djp.request
    is_ajax    = request.is_ajax()
    POST       = request.POST
    cont       = POST.has_key("_save_and_continue")
    url        = djp.url
    curr       = POST.get("_current_url",None)
    next       = POST.get("next",None)
    
    if POST.has_key("_cancel"):
        redirect_url = next
        if not redirect_url:
            if djp.instance:
                redirect_url = view.appmodel.viewurl(request,djp.instance)
            if not redirect_url:
                redirect_url = view.appmodel.searchurl(request) or '/'

        if is_ajax:
            return jredirect(url = redirect_url)                
        else:
            return http.HttpResponseRedirect(redirect_url)
    
    f      = view.get_form(djp)
    if f.is_valid():
        try:
            instance = view.save(request, f)
            smsg     = getattr(view,'success_message',success_message)
            msg      = smsg(instance, 'changed' if editing else 'added')
            f.add_message(request, msg)
        except Exception, e:
            f.add_message(request,e,error=True)
            if is_ajax:
                return f.json_errors()
            elif next:
                return http.HttpResponseRedirect(next)
            else:
                return view.handle_response(djp)
        
        if cont:
            if is_ajax:
                return f.json_message()
        else:
            redirect_url = next
            if not redirect_url:
                if hasattr(view,'appmodel'):
                    if instance:
                        redirect_url = view.appmodel.viewurl(request,instance) or view.appmodel.baseurl
                    else:
                        redirect_url = view.appmodel.baseurl
            if redirect_url and redirect_url == curr and is_ajax:
                return f.json_message()
            
        # We are Redirecting
        if redirect_url:
            if is_ajax:
                f.force_message(request)
                return jredirect(url = redirect_url)                
            else:
                return http.HttpResponseRedirect(redirect_url)
        else:
            if is_ajax:
                return f.json_message()      
            else:
                return view.handle_response(djp)
    else:
        if is_ajax:
            return f.json_errors()
        else:
            return view.handle_response(djp)
        
