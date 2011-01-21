import sys
import logging
from datetime import datetime

from djpcms import sites, forms
from djpcms.contrib import messages
from djpcms.utils.translation import ugettext_lazy as _
from djpcms.utils import force_str, gen_unique_id
from djpcms.utils.dateformat import format
from djpcms.utils.ajax import jredirect, jremove

from .htmlold import input


logger = logging.getLogger('djpcms.forms')

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
        data = dict(getattr(request,method).items())
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
    return add_extra_fields(form,name,forms.CharField(widget=forms.HiddenInput, required = required))


def success_message(instance, mch):
    dt = datetime.now()
    c = {'dt': format(dt,sites.settings.DATETIME_FORMAT),
         'mch': mch,
         'obj': instance}
    if instance:
        c['name'] = force_str(instance._meta.verbose_name)
        return _('The %(name)s "%(obj)s" was succesfully %(mch)s %(dt)s') % c
    else:
        return _('%(mch)s %(dt)s') % c


def update_initial(request, form_class, initial = None,
                   own_view = True):    
    if request.method == 'GET':
        params = dict(request.GET.items())
        next   = params.get('next',None)
        if not next and not own_view:
            next = request.path
        if next:
            form_class = add_hidden_field(form_class,'next')
        initial = initial or {}
        initial['next'] = next
    return initial


def get_form(djp,
             form_class,
             method = 'POST',
             initial = None,
             prefix = None,
             addinputs = None,
             withdata = True,
             instance  = None,
             model = None,
             form_withrequest = None,
             template = None,
             form_ajax = False,
             withinputs = False):
    '''Comprehensive method for building a
:class:`djpcms.utils.uniforms.UniForm` instance:
    
:parameter djp: instance of :class:`djpcms.views.DjpResponse`.
:parameter form_class: required form class.
:parameter method: optional string indicating submit method. Default ``POST``.
:parameter initial: If not none, a dictionary of initial values.
:parameter prefix: Optional prefix string to use in the form.
:parameter addinputs: An optional function for creating inputs.
                      If available, it is called if the
                      available form class as no inputs associated with it.
                      Default ``None``.
'''
    from djpcms.utils.uniforms import UniForm
    request  = djp.request
    own_view = djp.own_view()
    
    data = request.POST if request.method == 'POST' else request.GET
    prefix = data.get('_prefixed',None)
    
    save_as_new = data.has_key('_save_as_new')
    initial  = update_initial(request, form_class, initial,
                              own_view = own_view)
    
    inputs = getattr(form_class,'submits',None)
    if inputs:
        inputs = [input(value = val, name = nam) for val,nam in inputs]
    elif addinputs:
        inputs = addinputs(instance, own_view)
        
    if not prefix:
        prefix = gen_unique_id()
        inputs.append(input(value = prefix, name = '_prefixed', type = 'hidden'))
                
    f     = form_class(**form_kwargs(request     = request,
                                     initial     = initial,
                                     instance    = instance,
                                     prefix      = prefix,
                                     withdata    = withdata,
                                     withrequest = form_withrequest,
                                     method      = method,
                                     own_view    = own_view,
                                     save_as_new = save_as_new,
                                     inputs      = inputs if withinputs else None))
        
    wrap = UniForm(f,
                   request  = request,
                   instance = instance,
                   action   = djp.url,
                   inputs   = inputs,
                   template = template,
                   save_as_new = save_as_new)
    if form_ajax:
        wrap.addClass(djp.css.ajax)
    wrap.is_ajax = request.is_ajax()
    if model:
        wrap.addClass(str(model._meta).replace('.','-'))
    return wrap

    
def saveform(djp, editing = False, force_redirect = False):
    '''Comprehensive save method for forms'''
    view = djp.view
    request = djp.request
    http = djp.http
    is_ajax = request.is_ajax()
    POST = request.POST
    GET = request.GET
    curr = request.environ.get('HTTP_REFERER')
    next = get_next(request)
    f = view.get_form(djp)
    
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
    
    if f.is_valid():
        try:
            editing  = editing if not POST.has_key('_save_as_new') else False
            instance = view.save(request, f)
            smsg     = getattr(view,'success_message',success_message)
            msg      = smsg(instance, 'changed' if editing else 'added')
            f.add_message(request, msg)
        except Exception, e:
            exc_info = sys.exc_info()
            logger.error('Form Error: %s' % request.path,
                         exc_info=exc_info,
                         extra={'request':request})
            f.add_message(request,e,error=True)
            if is_ajax:
                return f.json_errors()
            elif next:
                return http.HttpResponseRedirect(next)
            else:
                return view.handle_response(djp)
        
        if POST.has_key('_save_and_continue'):
            if is_ajax:
                return f.json_message()
            else:
                redirect_url = curr
        else:
            redirect_url = view.defaultredirect(request,
                                                next = next,
                                                instance = instance)
            
            # not forcing redirect. Check if we can send a json message
            if not force_redirect:
                if redirect_url == curr and is_ajax:
                    return f.json_message()
            
        # We are Redirecting
        if is_ajax:
            f.force_message(request)
            return jredirect(url = redirect_url)
        else:
            return http.HttpResponseRedirect(redirect_url)
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
    msg     = 'Successfully deleted %s' % instance
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

