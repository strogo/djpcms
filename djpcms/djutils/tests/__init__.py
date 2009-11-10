from unittest import TestCase

from django.contrib.contenttypes.models import ContentType
from django.db.models import get_apps, get_models


class BaseDbTest(TestCase):
    
    def testContentTypes(self):
        for app in get_apps():
            ContentType.objects.clear_cache()
            content_types = list(ContentType.objects.filter(app_label=app.__name__.split('.')[-2]))
            app_models = get_models(app)
            if not app_models:
                return
            update_contenttypes(app, None, verbosity)
        ccys = currencydb()
        iso = {}
        for ccy in ccys.values():
            self.assertFalse(iso.has_key(ccy.isonumber))
            iso[ccy.isonumber] = ccy