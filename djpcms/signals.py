from django.db.models import signals

from djpcms.models import Page, Template, BlockContent


def hook_clear_cache(sender, **kwargs):
    if hasattr(sender.objects,'clear_cache'):
        sender.objects.clear_cache()
    
    
signals.post_save.connect(hook_clear_cache)



