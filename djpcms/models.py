from djpcms import sites

if sites.settings.CMS_ORM == 'django':
    
    from djpcms.core.cmsmodels._django import *
    
elif sites.settings.CMS_ORM == 'stdnet':
    
    from djpcms.core.cmsmodels._stdnet import *
    
else:
    
    raise NotImplementedError('Objecr Relational Mapper {0} not available for CMS models'.format(sites.settings.CMS_ORM))