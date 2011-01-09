import os

settings = object()

FLOWREPO_DATE_FORMAT = getattr(settings, 'FLOWREPO_DATE_FORMAT', '%a %d %b %Y')
FLOWREPO_TIME_FORMAT = getattr(settings, 'FLOWREPO_TIME_FORMAT', '%H:%M')
FLOWREPO_DATE_TIME_FORMAT = FLOWREPO_DATE_FORMAT + ' ' + FLOWREPO_TIME_FORMAT
FLOWREPO_SHOW_MARKUP_CHOICE = getattr(settings, 'FLOWREPO_HIDE_MARKUP_CHOICE', True)

FLOWREPO_STORAGE_IMAGE      = getattr(settings,
                                      'FLOWREPO_STORAGE_IMAGE',
                                      None)
FLOWREPO_STORAGE_ATTACHMENT = getattr(settings,
                                      'FLOWREPO_STORAGE_ATTACHMENT',
                                      None)
FLOWREPO_UPLOAD_FUNCTION    = getattr(settings, 'FLOWREPO_UPLOAD_FUNCTION', None)
FLOWREPO_THUMBNAILS_SIZE    = 64

FLOWREPO_PROVIDERS     = getattr(settings, 'FLOWREPO_PROVIDERS', ['flowrepo.providers.*'])
FLOWREPO_DIGIT_MONTH   = False

FLOWREPO_CODE_LINENO   = False

FOR_USER_ID              = getattr(settings, 'FOR_USER_ID', 1)
FLOWREPO_ADJUST_DATETIME = getattr(settings, 'FLOWREPO_ADJUST_DATETIME', False)

#TWITTER SETTINGS
TWITTER_CONSUMER_TOCKEN = getattr(settings, 'TWITTER_CONSUMER_TOCKEN', None)
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', None)
TWITTER_USERNAME       = getattr(settings, 'TWITTER_USERNAME', None)
TWITTER_RETWEET_TXT    = getattr(settings, 'TWITTER_RETWEET_TXT', 'From %s')
TWITTER_TRANSFORM_MSG  = getattr(settings, 'TWITTER_TRANSFORM_MSG', True)
TWITTER_REMOVE_LINKS   = getattr(settings, 'TWITTER_REMOVE_LINKS', False)
TWITTER_REMOVE_TAGS    = getattr(settings, 'TWITTER_REMOVE_TAGS', False)
DELICIOUS_GETDNS       = True
DELICIOUS_USERNAME     = getattr(settings, 'DELICIOUS_USERNAME', None)
DELICIOUS_PASSWORD     = getattr(settings, 'DELICIOUS_PASSWORD', None)


restmarkup = {'extensions':['pngmath']}
creolemarkup = {'extensions':[]}
markdownmarkup = {}

MARKUP_CONFIG = {'rst':restmarkup,
                 'crl':creolemarkup,
                 'md':markdownmarkup}

#LATEX SETTINGS
curdir = os.path.join(os.path.dirname(__file__),'markups','latex','workspace')
LATEX_PYTHON_PATH = getattr(settings,'LATEX_CLASSES_PATH',os.path.join(curdir,'src'))
LATEX_TEMPLATE_PATH = getattr(settings,'LATEX_CLASSES_PATH',os.path.join(curdir,'render'))
LATEX_TEX_PATH = getattr(settings,'LATEX_CLASSES_PATH',os.path.join(curdir,'tex'))
