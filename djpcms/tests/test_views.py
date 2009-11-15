import datetime

from django.test import TestCase
from django.conf import settings

from djpcms.models import SiteContent


class CalendarViewTest(TestCase):
    fixtures = ["sitecontent.json"]
        
    def callView(self, url):
        today = datetime.date.today()
        response = self.client.get(today.strftime(url).lower())
        if isinstance(response.context, list):
            context = response.context[0]
        else:
            context = response.context
        return today, response, context