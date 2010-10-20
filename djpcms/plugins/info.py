from djpcms.template import loader
from djpcms.plugins import DJPplugin
from djpcms.utils import version


class PoweredBy(DJPplugin):
    name = 'poweredby'
    description = 'Powered by panel'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        '''
        Information about the packages used to power the web-site
        '''
        v = version.get()
        p = v.pop('python')
        d = v.pop('django')
        c = {'python': p.get('version'),
             'django': d.get('version'),
             'other':  v.values()}
        return loader.render_to_string(['/bits/powered_by.html',
                                        'djpcms/bits/powered_by.html'],
                                        c)
        
class Deploy(DJPplugin):
    '''Information about deployment. Based on :class:`djpcms.contrib.jdep.models.DeploySite`.
If `djpcms.contrib.jdep` is not part of your ``INSTALLED_APPS``
nothing will be displayed.
    '''
    name = 'deploysite'
    description = 'Deploy Timestamp'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        from djpcms.conf import settings
        from djpcms.utils import timezone
        if 'djpcms.contrib.jdep' in settings.INSTALLED_APPS:
            from djpcms.contrib.jdep.models import DeploySite
            try:
                latest = DeploySite.objects.latest()
            except:
                return ''
            return loader.render_to_string(['/bits/deploy.html',
                                            'djpcms/bits/deploy.html'],
                                            {'latest':latest,
                                             'name': timezone.tzname(dt = latest.created),
                                             'url': timezone.link()})
        else:
            return ''
