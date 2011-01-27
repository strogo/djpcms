from django.contrib.auth.models import User
from django.db.models import signals

from djpcms.conf import settings
from djpcms.forms.cms import Page, create_page


def create_user_page(sender, instance, **kwargs):
    if isinstance(instance,User):
        filter = Page.objects.filter
        parent = filter(url = settings.USER_ACCOUNT_HOME_URL)
        if parent:
            parent = parent[0]
            pages = filter(parent = parent, url_pattern = instance.username)
            if pages:
                if pages.count() == 1:
                    return pages[0]
                else:
                    logger.error('It seems there are more than one home page page associate with user %s' % instance)
                    return page[0]
            return create_page(parent = parent,
                               user = instance,
                               url_pattern = instance.username,
                               title = instance.username,
                               link = instance.username,
                               soft_root = True)


def delete_user_page(sender, instance, **kwargs):
    if isinstance(instance,User):
        try:
            parent = Page.objects.get(url = settings.USER_ACCOUNT_HOME_URL)
        except Page.DoesNotExist:
            return
        page = Page.objects.filter(url = instance.username, parent = parent)
        page.delete()


signals.post_save.connect(create_user_page, sender = User)
signals.post_delete.connect(delete_user_page, sender = User)