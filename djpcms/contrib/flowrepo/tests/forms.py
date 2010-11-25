from django.test import TestCase
from django.contrib.auth.models import User

from djpcms.contrib.flowrepo.models import Report, FlowItem

__all__ = ['FormTest']


class FormTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@testuser.com', 'testuser')
    
    def testAdd(self):
        from flowrepo.forms import ReportForm
        f = ReportForm(user = self.user,
                       data = {'title': 'A test report',
                               'body': 'this is the body',
                               'tags': 'test report flow',
                               'visibility': 3})
        valid = f.is_valid()
        self.assertTrue(f.is_valid())
        r = f.save()
        self.assertTrue(isinstance(r,FlowItem))
        self.assertEqual(r.tags,'test report flow')
        