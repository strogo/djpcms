from werkzeug import wrappers
from werkzeug import exceptions

Request = wrappers.Request
HTTPResponse = wrappers.Response

HTTPException = exceptions.HTTPException
Http404 = exceptions.NotFound



