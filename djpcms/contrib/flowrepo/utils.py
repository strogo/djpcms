from os import urandom
from base64 import b64encode, b64decode

from django.conf import settings
from django.utils.dateformat import format, time_format
from django.utils.encoding import smart_str
from django.forms.util import flatatt

from PIL import Image


def encrypt(plaintext):
    from Crypto.Cipher import ARC4
    if not plaintext:
        return u''
    salt = urandom(settings.SALT_SIZE)
    arc4 = ARC4.new(salt + settings.SECRET_KEY)
    prnd = smart_str(urandom(256-len(plaintext)))
    plaintext = smart_str("%3d%s" % (len(plaintext), plaintext))
    plaintext = plaintext + prnd
    return "%s$%s" % (b64encode(salt), b64encode(arc4.encrypt(plaintext)))


def decrypt(ciphertext):
    from Crypto.Cipher import ARC4
    if ciphertext:
        salt, ciphertext = map(b64decode, ciphertext.split('$'))
        arc4 = ARC4.new(salt + settings.SECRET_KEY)
        plaintext = arc4.decrypt(ciphertext)
        return plaintext[3:3+int(plaintext[:3].strip())]
    else:
        return u''
    
    
fudge  = 1.25
hour   = 60.0 * 60.0
day    = hour * 24.0
week   = 7.0 * day
month  = 30.0 * day
def nicetimedelta(date1, date0):
    tdelta  = date1 - date0
    days    = tdelta.days
    sdays   = day * days
    delta   = tdelta.seconds + sdays
    if delta < fudge:
        return u'about a second ago'
    elif delta < (60.0 / fudge):
        return u'about %d seconds ago' % int(delta)
    elif delta < (60.0 * fudge):
        return u'about a minute ago'
    elif delta < (hour / fudge):
        return u'about %d minutes ago' % int(delta / 60.0)
    elif delta < (hour * fudge):
        return u'about an hour ago'
    elif delta < day:
        return u'about %d hours ago' % int(delta / hour)
    else:
        return u'%s %s' % (format(date0, settings.DATE_FORMAT),time_format(date0.time(), settings.TIME_FORMAT))
    
    
class htmlattr(object):
    styles = ['float','width','height']
    def __init__(self, kwargs = None):
        self.attrs = {}
        self.style = {}
        if kwargs:
            self.update(kwargs)
    
    def update(self, kwargs):
        for k,v in kwargs.items():
            if k in self.styles:
                self.style[k] = v
            else:
                self.attrs[k] = v
            
    def flatstyle(self):
        st = []
        for k,v in self.style.items():
            st.append('%s: %s;' % (k,v))
        return ' '.join(st)
    
    def flat(self):
        if self.style:
            self.attrs['style'] = self.flatstyle()
        if self.attrs:
            return flatatt(self.attrs)
        return ''
    
def thumbnails(image, size):
    image.thumbnail(size, Image.ANTIALIAS)
    return image