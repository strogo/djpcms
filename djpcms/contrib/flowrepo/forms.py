from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from djpcms.views.apps.tagging import TagField

from djpcms import forms
from djpcms.utils import json
from djpcms.contrib.flowrepo import models



def get_upload_model(file):
    '''Upload model'''
    try:
        from PIL import Image
    except ImportError:
        import Image

    model = models.Attachment
    try:
        if file.content_type.split('/')[0] == 'image':
            model = models.Image
        #trial_image = Image.open(file)
        #trial_image.load()
        #trial_image.verify()
        #model = models.Image
    except:
        model = models.Attachment
    
    return model



class FlowForm(forms.ModelForm):
    '''General form for a flowitem'''
    _underlying = None
    timestamp = forms.DateTimeField(required = False)
    tags      = TagField(required = False)
    
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user',None)
        super(FlowForm,self).__init__(*args, **kwargs)
        
    class Meta:
        model = models.FlowItem
    
    def savemodel(self, obj):
        raise NotImplementedError()
    
    def get_user(self):
        return self._user or self.request.user
        
    def save(self, commit = True):
        user       = self.get_user()
        model      = self._underlying
        instance   = self.instance
        instance.content_type = ContentType.objects.get_for_model(model)
        flowitems  = models.FlowItem.objects
        registered = flowitems.unregisterModel(model)
        if instance.object_id:
            object     = instance.object
        else:
            object     = model()
        instance.object_id = self.savemodel(object).id
        instance   = super(FlowForm,self).save(commit = commit)
        instance.authors.add(user)
        if registered:
            flowitems.registerModel(model)
        return instance


class FlowFormRelated(FlowForm):
    '''handle related items as multiple choice field'''
    related_items = forms.ModelMultipleChoiceField(queryset = models.FlowItem.objects.all(), required = False)
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance',None)
        if instance:
            initial = kwargs.get('initial',None) or {}
            initial['related_items'] = [obj.related.id for obj in instance.following.all()]
            kwargs['initial'] = initial
        super(FlowFormRelated,self).__init__(*args, **kwargs)
            
    def save(self, commit = True):
        instance = super(FlowFormRelated,self).save(commit = True)
        if commit:
            instance.following.all().delete()
            for related in self.cleaned_data['related_items']:
                instance.follow(related)
        return instance
    

class ReportForm(FlowFormRelated):
    '''The Report Form'''
    _underlying = models.Report
    title = forms.CharField()
    abstract = forms.CharField(widget = forms.Textarea(attrs = {'class':'taboverride'}), required = False)
    body  = forms.CharField(widget = forms.Textarea(attrs = {'class':'taboverride'}), required = False)
    slug  = forms.CharField(required = False)
    
    class Meta:
        model = models.FlowItem
        exclude = ['name','description','url','groups']
        
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance',None)
        if instance:
            obj = instance.object
            initial = kwargs.get('initial',None) or {}
            initial['title'] = getattr(obj,'name',instance.name)
            initial['abstract'] = getattr(obj,'description',instance.description)
            initial['body'] = getattr(obj,'body','')
            kwargs['initial'] = initial
        super(ReportForm,self).__init__(*args,**kwargs)
        
    def savemodel(self, obj):
        obj.name = self.cleaned_data['title']
        obj.description = self.cleaned_data['abstract']
        obj.body = self.cleaned_data['body']
        obj.save()
        return obj   
    

class UploadForm(FlowForm):
    elem = forms.FileField(label = 'file')
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance',None)
        if instance:
            self._underlying = instance.content_type.model_class()
        super(UploadForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = models.FlowItem
        exclude = ['timestamp','authors','groups','url']
        
    def savemodel(self, obj):
        obj.name = self.instance.name
        obj.elem = self.cleaned_data['elem']
        obj.save()
        return obj        
    
    def clean_elem(self):
        file = self.cleaned_data.get('elem')
        model = get_upload_model(file)
        if self._underlying and model is not self._underlying:
            raise forms.ValidationError('Cannot change upload type')
        self._underlying = model
        return file


class FlowItemSelector(forms.ModelForm):
    '''
    Form for selecting items to display
    '''
    content_type = forms.ModelMultipleChoiceField(queryset = models.FlowItem.objects.allmodels,
                                                  label = 'types',
                                                  required = False)
    item_per_page = forms.IntegerField(initial = 10)
    
    class Meta:
        model = models.FlowItem
        fields = ('content_type', 'visibility', 'tags')
        
    def save(self, commit = True):
        pass

        
class WebAccountForm(forms.ModelForm):
    '''A form to add/edit web accounts.
    '''
    user     = forms.CharField(widget=forms.HiddenInput, required = False)
    username = forms.CharField(required = False, max_length = 200)
    password = forms.CharField(required = False, max_length = 200)
    email    = forms.EmailField(required = False)
    pin      = forms.CharField(required = False, max_length = 200)
    extended = forms.CharField(required = False)
    tags     = TagField(required = False)
    
    def __init__(self, **kwargs):
        request = kwargs.get('request',None)
        instance = kwargs.get('instance',None)
        self._user = request.user
        if instance:
            data = instance.data
            if data:
                initial = kwargs.get('initial',None) or {}
                initial.update(json.loads(data))
                kwargs['initial'] = initial
        super(WebAccountForm,self).__init__(**kwargs)
        
    class Meta:
        model   = models.WebAccount
        exclude = ['e_data']
    
    def clean_user(self):
        return self._user
    
    def clean_name(self):
        user = self._user
        name = self.cleaned_data['name']
        if name:
            acc = self._meta.model.objects.filter(user = user, name = name)
            if acc:
                acc = acc[0]
                if acc.id != self.instance.id:
                    raise forms.ValidationError('Account %s already available' % name)
            return name
        else:
            raise forms.ValidationError('Account name is required')
        
    def tojson(self):
        if self.is_valid():
            return json.dumps(self.cleaned_data)
        else:
            return u''
        
    def save(self, commit = True):
        if commit:
            data = self.cleaned_data.copy()
            for n in ('user','name','url','tags'):
                data.pop(n)
            self.instance.data = json.dumps(data)
        return super(WebAccountForm,self).save(commit)
    

class ChangeCategory(forms.Form):
    category_name = forms.ModelChoiceField(queryset = models.CategoryType.objects.all(),
                                           empty_label=None)
    
    
class ChangeImage(forms.Form):
    image   = forms.ModelChoiceField(queryset = models.Image.objects.all(), empty_label=None)
    class_name = forms.CharField(max_length = 100, required = False)
    
    
def add_related_upload(file, instance, name = None, description = ''):
    item = instance.flowitem()
    if not item or not file:
        return
    model = get_upload_model(file)    
    name = name or file.name
    obj = model(elem = file, name = name, description = description)
    obj.save()
    return models.FlowRelated.objects.create_for_object(item,obj)
    
    
    
