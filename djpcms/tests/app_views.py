from django.contrib.auth.models import User

from djpcms.test import TestCase
from djpcms.conf import settings

from testmodel.models import Strategy


class TestAppViews(TestCase):
    
    def testParents(self):
        appmodel = self.site.for_model(Strategy)
        search = appmodel.getview('search')
        view = appmodel.getview('view')
        self.assertTrue(view.parent,search)
        edit = appmodel.getview('edit')
        self.assertTrue(edit.parent,view)