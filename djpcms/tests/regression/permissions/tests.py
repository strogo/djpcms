from django.contrib.auth.models import User

from djpcms.test import TestCase
from djpcms.conf import settings


class TestPage(TestCase):
    
    def testEditPageLink(self):
        editlink = '<a class="edit-page-link" title="edit page contents" href="/edit-content/">edit</a>'
        res  = self.get(response = True)
        page = res.context['page']
        self.assertEqual(page.url,'/')
        html = res.content
        self.assertFalse(editlink in html)
        self.login()
        res  = self.get(response = True)
        html = res.content
        self.assertTrue(editlink in html)
        
    def testEditDenied(self):
        self.get('/edit-content/', status = 403)
        self.login()
        res = self.get('/edit-content/', response = True)