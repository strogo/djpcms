from djpcms.utils import urlfrombits, urlbits

def view_edited_url(path):
    return urlfrombits(urlbits(path)[1:])