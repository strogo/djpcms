from django.conf import settings

RECAPTCHA_PUB_KEY = getattr(settings,"RECAPTCHA_PUB_KEY",None)
RECAPTCHA_PRIVATE_KEY = getattr(settings,"RECAPTCHA_PRIVATE_KEY",None)