from django.contrib.auth.models import User

from djpcms.test import TestCase
from djpcms.conf import settings
    
    
class TestStyling(TestCase):
    
    def testDefaultStyle(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code,200)
        context = response.context
        media = context["media"]
        self.assertTrue(media)
        allcss = str(media)
        self.assertTrue(settings.DJPCMS_STYLE in allcss)
        self.assertTrue('djpcms/jquery-ui-css/%s' % settings.DJPCMS_STYLE in allcss)
        self.assertTrue('djpcms/tablesorter/themes/%s' % settings.DJPCMS_STYLE in allcss)
        self.assertTrue('djpcms/themes/%s' % settings.DJPCMS_STYLE in allcss)


class TestNoStyle(TestCase):
    
    def setUp(self):
        self.style = settings.DJPCMS_STYLE
        settings.DJPCMS_STYLE = None
        
    def testNoStyle(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code,200)
        media = response.context["media"]
        self.assertTrue(media)
        css = media._css
        self.assertFalse(css)
        
    def tearDown(self):
        from djpcms.conf import settings
        settings.DJPCMS_STYLE = self.style
        

class TestCustomStyle(TestCase):
    
    def setUp(self):
        settings.DJPCMS_STYLING_FUNCTION = 'regression.style.other.test_styling_function'
        User.objects.create_user('pinco', 'pinco@pinco.com', 'pinco')
        
    def testCusomStyle(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code,200)
        media = response.context["media"]
        self.assertTrue(media)
        css = media._css['all'][0]
        self.assertEqual(css,'djpcms/unknown.css')
        
        self.assertTrue(self.client.login(username = 'pinco', password = 'pinco'))
        response = self.client.get('/')
        media = response.context["media"]
        self.assertTrue(media)
        css = media._css['all'][0]
        self.assertEqual(css,'djpcms/authenticated.css')
        
    def tearDown(self):
        from djpcms.conf import settings
        settings.DJPCMS_STYLING_FUNCTION = None
    