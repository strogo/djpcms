from djpcms.conf import settings

if settings.CMS_ORM == 'django':
    
    from djpcms.core.cmsmodels._django import *
    
elif settings.CMS_ORM == 'stdnet':
    
    from djpcms.core.cmsmodels._stdnet import *
    
else:
    
    raise NotImplementedError('Objecr Relational Mapper {0} not available for CMS models'.format(settings.CMS_ORM))