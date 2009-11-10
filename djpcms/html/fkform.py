'''
Create Form for Foreign key models
'''

from base import div
from form import formlet

__all__ = ['fkform','makefkforms']


def get_manager(model, fkmodel):
    setname = '%s_set' % fkmodel._meta.module_name
    return getattr(model,setname)


def makefkforms(model    = None,
                object   = None,
                fkmodel  = None,
                extra    = 3,
                blank    = True,
                **attrs):
    co = div()
    count = 0
    if object: 
        manager = get_manager(object,fkmodel)
        count   = 0
        for fk in manager.all():
            co.append(fkform(prefix   = count,
                             object   = fk,
                             blank    = blank,
                             **attrs))
            count += 1
    
    extra = max(extra-count,3) + count
    for i in range(count,extra):
            co.append(fkform(prefix   = i,
                             model    = fkmodel,
                             blank    = blank,
                             **attrs))                
    return co

class fkform(formlet):
    '''
    Forlmlet for a foreignKey
    '''
    def __init__(self, blank = True, **attrs):
        self.blank   = blank
        super(fkform,self).__init__(**attrs)
        
    def is_valid(self):
        '''
        Check if form is valid.
        If not fill the ajax errors dictionary
        '''
        if self.blank:
            self.form.is_valid()
            return True
        else:
            super(fkform,self).is_valid()
            
    def save(self):
        '''
        Overwrite the save method so we can add the foreignkey
        '''
        if self.form.is_valid():
            return self.form.save()
        