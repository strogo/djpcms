from django.conf import settings
from django.core.files import storage

from s3boto import S3BotoStorage

class SiteFileSystemStorage(storage.FileSystemStorage):
    
    def __init__(self, location = None, base_url = None):
        if base_url is None:
            base_url = '%ssite/' % settings.MEDIA_URL
        super(SiteFileSystemStorage,self).__init__(location = location, base_url = base_url)