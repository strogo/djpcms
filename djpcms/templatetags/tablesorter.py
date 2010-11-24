from django import template
from djpcms.views.changelist import ChangeList, table
from djpcms.core.models import nicerepr

register = template.Library()

@register.inclusion_tag('djpcms/tablesorter.html')
def totable(headers, queryset, djp = None, appmodel = None, nd = 3):
    return table(headers, queryset, djp, appmodel, nd)

@register.filter
def nicevalue(value, nd = 3):
    return nicerepr(value, nd)
    