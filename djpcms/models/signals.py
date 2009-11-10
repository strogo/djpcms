from django.db.models import signals

from page import Page, Template
from contentplugins import BlockContent

def update_plugin_positions(sender, instance = None, **kwargs):
    if sender == Template:
        nblocks = instance.numblocks()
        pages = Page.objects.filter(inner_template = instance)
    elif sender == Page:
        nblocks = instance.inner_template.numblocks()
        pages = [instance]
    else:
        return
        
    for p in pages:
        cs = BlockContent.objects.filter(page = p, block__gte = nblocks)
        cs.delete()
        
signals.post_save.connect(update_plugin_positions, sender=Page)
signals.post_save.connect(update_plugin_positions, sender=Template)