from django.conf import settings
from compressor import storage

class CompressorFileStorage(storage.CompressorFileStorage):
    
    def path(self, name):
        '''
        Given a relative path to a file return the absolute path to the file
        '''
        try:
            path = safe_join(self.location, name)
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." % name)
        return smart_str(os.path.normpath(path))
    