import datetime

from djpcms import test


class CalendarViewTest(test.TestCase):
    appurls  = 'regression.apparchive.appurls'
        
    def callView(self, url):
        today = datetime.date.today()
        response = self.client.get(today.strftime(url).lower())
        if isinstance(response.context, list):
            context = response.context[0]
        else:
            context = response.context
        return today, response, context
    
    def testYearView(self):
        today, response, context = self.callView("/content/%Y/")
        pa = context["paginator"]
        self.assertEqual(int(context["year"]), today.year)
        self.assertEqual(pa.total,
                         SiteContent.objects.filter(last_modified__year = today.year).count())
        
    def testMonthView(self):
        today, response, context = self.callView("/content/%Y/%b/")
        pa = context["paginator"]
        self.assertEqual(int(context["year"]), today.year)
        #self.assertEqual(context["month"], today.month)
        self.assertEqual(pa.total,
                         SiteContent.objects.filter(last_modified__year  = today.year,
                                                    last_modified__month = today.month).count())
        
    def testDayView(self):
        today, response, context = self.callView("/content/%Y/%b/%d/")
        pa = context["paginator"]
        self.assertEqual(int(context["year"]), today.year)
        #self.assertEqual(context["month"], today.month)
        self.assertEqual(int(context["day"]), today.day)
        self.assertEqual(pa.total,
                         SiteContent.objects.filter(last_modified__year  = today.year,
                                                    last_modified__month = today.month,
                                                    last_modified__day   = today.day).count())

