from datetime import date

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.dates import MONTHS

from djpcms.utils import force_unicode
from djpcms.template import loader
from djpcms.plugins import DJPplugin
from djpcms.views import appsite


def all_archive_model():
    from djpcms.views.apps.archive import ArchiveApplication
    ids = []
    for model,app in appsite.site._registry.items():
        if isinstance(app,ArchiveApplication):
            ct = ContentType.objects.get_for_model(model)
            ids.append(ct.id)
    return ContentType.objects.filter(pk__in = ids)

class ArchiveForm(forms.Form):
    for_model = forms.ModelChoiceField(all_archive_model())


def filter_date(app, y, m):
    y1 = y
    m1 = m + 1
    if m1 > 12:
        m1 = 1
        y1 = y + 1
    return app.model.objects.filter(**{'%s__lt' % app.date_code: date(y1,m1,1)})


class ArchiveList(DJPplugin):
    form = ArchiveForm
    
    def render(self, djp, wrapper, prefix, for_model = None, start = None, **kwargs):
        try:
            formodel = ContentType.objects.get(id = int(for_model)).model_class()
            app = appsite.site.for_model(formodel)
        except:
            return u''
        request = djp.request
        start = None or date.today()
        year  = start.year
        month = start.month
        equal  = lambda qs, y, m :qs.filter(**{'%s__year' % app.date_code: y,
                                               '%s__month' % app.date_code: m})
        qs = filter_date(app,year,month)
        py = year
        months = []
        years  = []
        T      = 0
        while qs.count():
            if year != py:
                if months:
                    url = app.yearurl(request, year)
                    years.append({'year':py, 'months':months, 'url': url, 'count': T})
                months = []
                T = 0
            py   = year
            data = equal(qs,year,month)
            N  = data.count()
            T += N
            if N:
                url = app.monthurl(request, year, month)
                months.append({'month':force_unicode(MONTHS[month]),'count':N,'url':url})
            month -= 1
            if month < 1:
                month  = 12
                year  -= 1
            qs = filter_date(app,year,month)
        return loader.render_to_string('djpcms/bits/archivelist.html', {'years':years})
    
    class Media:
        js = ['djpcms/archive.js']
    