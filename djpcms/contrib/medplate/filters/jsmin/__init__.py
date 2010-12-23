from djpcms.contrib.compressor.filters.jsmin.jsmin import jsmin
from djpcms.contrib.compressor.filters import FilterBase

class JSMinFilter(FilterBase):
    def output(self, **kwargs):
        return jsmin(self.content)