
from .builder import Api, api_method

def social_yahoo_api_method(post_data = None, **kwargs):
    post_data = post_data or {}
    post_data['format'] ='json'
    return api_method(host = 'social.yahooapis.com', api_root = '/v1',
                      secure = False, post_data = post_data,
                      **kwargs)

def delicious_api_method(post_data = None, **kwargs):
    post_data = post_data or {}
    post_data['format'] ='json'
    return api_method(host = 'api.del.icio.us', api_root = '/v2',
                      secure = True, **kwargs)


class YahooApi(Api):
    """Yahoo API"""

    user_id = social_yahoo_api_method(path = '/me/guid',
                                      postprocess = lambda data : data['guid']['value'])
    user_data = social_yahoo_api_method(path = '/user/{0}/profile',
                                        postprocess = lambda data : data['profile'])
    delicious_update = delicious_api_method(path = '/posts/update')