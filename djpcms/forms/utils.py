from datetime import datetime

from django import http
from django.utils.dateformat import format
from djpcms.contrib import messages
from django.utils.translation import ugettext_lazy as _

from djpcms.utils.html import submit
from djpcms.utils import force_unicode
from djpcms.utils.ajax import jredirect, jremove


get_next = lambda request, name = "next" : request.POST.get(name,request.GET.get(name,None))


def next_and_current(request):
    next = get_next(request)
    curr = request.environ.get('HTTP_REFERER')
    if next:
        next = request.build_absolute_uri(next)
    return next,curr


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

    
def saveform(djp, editing = False, force_redirect = False):
    '''Comprehensive save method for forms'''
    view       = djp.view
    request    = djp.request
    is_ajax    = request.is_ajax()
    POST       = request.POST
    GET        = request.GET
    cont       = POST.has_key("_save_and_continue")
    url        = djp.url
    curr       = request.environ.get('HTTP_REFERER')
    next       = get_next(request)
    if next:
        next = request.build_absolute_uri(next)
    
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
            if not force_redirect:
                if redirect_url and redirect_url == curr and is_ajax:
                    return f.json_message()
            else:
                redirect_url = redirect_url or '/'
            
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
        

def deleteinstance(djp, force_redirect = False):
    '''Delete an instance from database'''
    instance = djp.instance
    view    = djp.view
    request = djp.request
    
    curr    = request.environ.get('HTTP_REFERER')
    next    = get_next(request)
    if next:
        next = request.build_absolute_uri(next)
    next = next or curr
        
    bid     = view.appmodel.remove_object(instance)
    msg     = 'Successfully deleted %s' % bid
    if request.is_ajax():
        if next == curr and bid and not force_redirect:
            return jremove('#%s' % bid)
        else:
            messages.info(request,msg)
            return jredirect(next)
    else:
        messages.info(request,msg)
        next = next or curr
        return http.HttpResponseRedirect(next)
    
    

def fill_form_data(f):
    '''Utility for filling a dictionary with data contained in a form'''
    data = {}
    initial = f.initial
    is_bound = f.is_bound
    for field in f:
        v = field.data
        if v is None and not is_bound:
             v = getattr(field.field,'initial',None)
             if v is None:
                 v = initial.get(field.name,None)
        if v is not None:
            data[field.html_name] = v
    return data 
