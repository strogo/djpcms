from django import template
from djpcms.views.changelist import ChangeList, table
from djpcms.core.models import nicerepr

register = template.Library()

@register.inclusion_tag('djpcms/tablesorter.html')
def totable(headers, queryset, djp, appmodel):
    return table(headers, queryset, djp, appmodel)

@register.filter
def nicevalue(value):
    return nicerepr(value)
    