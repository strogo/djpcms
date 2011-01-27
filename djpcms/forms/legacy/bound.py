

class BoundForm(object):
    '''Class holding a form, formsets and helper for displaying forms as uni-forms.'''
    default_template = 'djpcms/uniforms/uniform.html'
    default_error_msg = 'There were errors. Try again.' 
    
    def __init__(self,
                 form,
                 template = None,
                 request = None,
                 instance = None,
                 method = 'post',
                 enctype = 'multipart/form-data',
                 error_message = None,
                 action = '.',
                 inputs = None,
                 tag = True,
                 csrf = True,
                 save_as_new  = False,
                 is_ajax = False):
        self.use_csrf_protection = csrf and default_csrf()
        self.attr = {}
        self.attr['method']  = method
        self.attr['action']  = ''
        self.attr['enctype'] = enctype
        self.attr['id']      = ''
        self.attr['class']   = 'uniForm'
        self.attr['action']  = action
        self.forms           = []
        self.formsets        = []
        self.inputs          = inputs or []
        self.tag             = tag
        self._messages       = []
        self._errors         = []
        self.save_as_new     = save_as_new
        self.prefix          = form.prefix
        self.is_ajax         = is_ajax
        self.error_message   = error_message if error_message is not None else self.default_error_msg
        self.template        = template or self.default_template
        self.add(form,request,instance)
    
    def add(self, form, request = None, instance = None):
        if not form:
            return False
        elif isinstance(form,BaseForm):
            form.layout = getattr(form,'layout',None) or FormLayout()
            instance = instance or getattr(form,'instance',None)
            self._build_fsets(form,request,instance)
            self.forms.append((form.layout,form))
        else:
            form = Html(form)
            self.forms.append((form,form))
        return True
    
    def __len__(self):
        return len(self.forms)
    
    def forms_only(self):
        for form in self.forms:
            if isinstance(form[1],BaseForm):
                yield form[1]
                
    def __getitem__(self, index):
        return self.forms[index][1]
    
    def __get_media(self):
        media = None
        for form in self.forms:
            fmedia = form[1].media
            media = fmedia if media is None else media + fmedia
        return media
    media = property(__get_media)
    
    def __get_instance(self):
        for form in self.forms:
            instance = getattr(form[1],'instance',None)
            if instance:
                return instance
        return None
    instance = property(__get_instance)
    
    def is_valid(self):
        valid = True
        for form in self.forms:
            form = form[1]
            if isinstance(form,BaseForm):
                if not form.is_valid():
                    all = form._errors.get('__all__')
                    if all:
                        if not self._errors:
                            self._errors = all
                        else:
                            self._errors.extend(all)
                    valid = False
        return valid and all_valid(self.formsets)
    
    def save(self, commit = True):
        '''Save the form's content wherever it needs to be stored.
Loops through the forms and call individual save methods if they are
available.

:parameter commit: if ``True`` changes are committed. Default ``True``.'''
        instances = None
        for form in self.forms:
            save = getattr(form[1],'save',None)
            if save:
                instance = save(commit = commit)
        if instance is not None and commit:
            for formset in self.formsets:
                formset.save(instance)
        if instance and getattr(instance,'id',None):
            return instance.__class__.objects.get(id = instance.id)
        else:
            return instance
    
    def add_message(self, request, msg, error = False):
        msg = str(msg)
        if msg:
            if error:
                self._errors.append(msg)
                if not self.is_ajax:
                    messages.error(request,msg)
            else:
                self._messages.append(msg)
                if not self.is_ajax:
                    messages.info(request,msg)
        return self
            
    def force_message(self, request):
        if self.is_ajax:
            for msg in self._messages:
                messages.info(request,msg)
            for msg in self._errors:
                messages.error(request,msg)
            
    def json_message(self):
        msg = self._make_messages('messagelist',self._messages)
        err = self._make_messages('errorlist',self._errors)
        return jhtmls(identifier = '.form-messages', html = msg+err, alldocument = False)
        
    def _formerrors(self, jerr, form):
        for name,errs in form.errors.items():
            errs = str(errs)
            field_instance = form.fields.get(name,None)
            if field_instance:
                bound_field = BoundField(form, field_instance, name)
                jerr.add('#%s-errors' % bound_field.auto_id,errs,alldocument = False)
        
    def json_errors(self, withmessage = True):
        '''Serialize form errors for AJAX-JSON interaction.
        '''
        jerr = jhtmls()
        for form in self.forms:
            form = form[1]
            if isinstance(form,BaseForm):
                self._formerrors(jerr, form)
        for formset in self.formsets:
            for form in formset.forms:
                self._formerrors(jerr, form)
        jerr.update(self.json_message())
        return jerr
    
    @property
    def cleaned_data(self):
        cd = {}
        for form in self.forms:
            cd.update(form[1].cleaned_data)
        return cd

    def render(self, djp = None, validate = False):
        '''Render the uniform by rendering individual forms, inline forms and inputs.'''
        fdict = {}
        forms = []
        num = 0
        inputs = self.render_inputs()
        for layout,form in self.forms:
            num += 1
            html = layout.render(form, inputs)
            forms.append(html)
            fdict['html%s' % num] = html
            
        cd = {'uniform': self,
              'errors': self._errors or '',
              'forms': forms,
              'fdict': fdict,
              'inputs': inputs,
              'inlines': self.render_inlines()}
        
        context_instance = None
        if djp:
            context_instance = RequestContext(djp.request, cd)
            cd = None
            djp.media += self.media
        if validate:
            self.is_valid()
            
        return loader.render_to_string(self.template,cd,
                                       context_instance)
        
    def render_inputs(self):
        if self.inputs:
            c = {'inputs':(mark_safe(s) for s in self.inputs)}
            return loader.render_to_string('djpcms/uniforms/inputs.html',c)
        else:
            return ''
    
    def render_inlines(self):
        if self.formsets:
            return loader.render_to_string('djpcms/uniforms/inlines.html',
                                           {'form_inlines': self.formsets,
                                            'field_class': inlineFormsets})
        else:
            return ''
    
    def _build_fsets(self, form, request, instance):
        '''Build formsets related to ``instance`` model'''
        formsets = self.formsets
        prefixes = {}
        fp = self.prefix
        if fp:
            fp += '-'
        for inline in form.layout.inlines:
            prefix  = fp + inline.get_default_prefix()
            prefixes[prefix] = p = prefixes.get(prefix, 0) + 1
            if p != 1:
                prefix = "%s-%s" % (prefix, p)
            formset = inline.get_formset(request = request,
                                         data     = form.data,
                                         instance = instance,
                                         prefix   = prefix,
                                         save_as_new = self.save_as_new)
            formsets.append(formset)
    
    def _make_messages(self, cname, mlist):
        if mlist:
            return mark_safe('<ul class="%s"><li>%s</li></ul>' % (cname,'</li><li>'.join(mlist)))
        else:
            return u''
            
    def htmldata(self):
        data = {}
        for form in self.forms:
            data.update(fill_form_data(form[1]))
        for fset in self.formsets:
            formset = fset.formset
            for f in formset.forms:
                data.update(fill_form_data(f))
            data.update(fill_form_data(formset.management_form))
        return data

