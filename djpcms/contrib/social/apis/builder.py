import json


class Api(object):

    def __init__(self, handler, access_token = None):
        self.handler = handler
        self.access_token = access_token
        
    def fetch(self, uri, parameters, method):
        req = self.handler.oauth_request(self.access_token,
                                         uri,
                                         extra_parameters = parameters)
        return self.handler.fetch_response(req, method)



class APIMethod(object):
    
    def __init__(self, config):
        self.secure    = config.pop('secure',False)
        self.method    = config.pop('method','GET')
        self.api_root  = config.pop('api_root','')
        self.path      = config.pop('path','')
        self.host      = config.pop('host',None)
        self.post_data = config.pop('post_data', None)
        self.headers = config.pop('headers', {})
        self.postprocess = config.pop('postprocess', lambda x : x)
        
        if self.secure:
            self.scheme = 'https://'
        else:
            self.scheme = 'http://'
            
        self.uri = self.scheme + self.host + self.api_root + self.path
        
    def __call__(self, api, args, kwargs):
        parameters = self.post_data or {}
        parameters.update(kwargs)
        uri  = self.uri.format(*args)
        data = api.fetch(uri, parameters, self.method)
        return self.postprocess(json.loads(data))
    

def api_method(**config):
    
    method = APIMethod(config)
    
    def _(api, *args, **kwargs):
        return method(api, args, kwargs)
    
    return _