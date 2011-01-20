

class NoData(object):
    def __repr__(self):
        return '<NoData>'
    __str__ = __repr__


class ValidationError(Exception):
    pass

nodata = NoData()