
__all__ = ['ModelDbAdmin']

class ModelDbAdmin(object):
    format = 'csv'
    def __init__(self, model, dbadmin):
        self.model   = model
        self.opts    = model._meta
        self.dbadmin = dbadmin