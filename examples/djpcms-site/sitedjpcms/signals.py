from django.contrib.auth.models import User
from django.db.models import signals

from djpcms.conf import settings
from djpcms.models import Page, create_page


def create_user_page(sender, instance, **kwargs):
    if isinstance(instance,User):
        parent = Page.objects.get(url = settings.USER_ACCOUNT_HOME_URL)
        return create_page(instance.username, parent = parent, user = instance, soft_root = True)


def delete_user_page(sender, instance, **kwargs):
    if isinstance(instance,User):
        parent = Page.objects.get(url = settings.USER_ACCOUNT_HOME_URL)
        page = Page.objects.filter(url = instance.username, parent = parent)
        page.delete()

signals.post_save.connect(create_user_page, sender = User)

signals.post_delete.connect(delete_user_page, sender = User)