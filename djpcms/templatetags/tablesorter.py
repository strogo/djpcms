from django import template
from djpcms.views.changelist import ChangeList, table

register = template.Library()

@register.inclusion_tag('djpcms/tablesorter.html')
def totable(queryset, djp, appmodel):
    return table(queryset, djp, appmodel)