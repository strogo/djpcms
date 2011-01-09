import oauth
from djpcms.contrib.social import OAuthProvider


DEFAULT_GOOGLE_SCOPE_SERVICES = ['http://finance.google.com/finance/feeds/']



class Google(OAuthProvider):
    REQUEST_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetRequestToken'
    AUTHORIZATION_URL = 'https://www.google.com/accounts/OAuthAuthorizeToken'
    ACCESS_TOKEN_URL  = 'https://www.google.com/accounts/OAuthGetAccessToken'
    
    def extra_request_parameters(self):
        scopes = getattr(self.settings,'GOOGLE_SCOPE_SERVICES',DEFAULT_GOOGLE_SCOPE_SERVICES)
        scopes_string = ' '.join((str(scope) for scope in scopes))
        return {'scope':scopes_string}
        
    def authenticated_api(self, key, secret):
        auth = GoogleApi(*self.tokens)
        api = GoogleApi(auth)
        api.set_access_token(key, secret)
        return api
        
    def client(self, key = None, secret = None, **kwargs):
        tks = {}
        ot  = OAuthToken(key, secret, self.scopes)
        for scope in self.scopes:
            tks[scope] = ot
        store = TokenStore(tks)
        pass
    
