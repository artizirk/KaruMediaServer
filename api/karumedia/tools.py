
import json

from falcon import Request as FalconRequest
from falcon import Response as FalconResponse
from falcon.errors import HTTPBadRequest, HTTPMissingParam, HTTPError
import falcon.status_codes as status


class JsonRequest(FalconRequest):

    #__slots__ = set(FalconRequest.__slots__ + ("_json", "_args"))


    @property
    def json(self):
        if not hasattr(self, "_json"):
            if not self.client_accepts_json:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports the JSON formated data')
            try:
                self._json = json.loads(self.stream.read().decode('utf8'))
            except json.decoder.JSONDecodeError as err:
                raise HTTPBadRequest("JSONDecodeError", str(err))
        return self._json


class JsonResponse(FalconResponse):

    #__slots__ = set(FalconRequest.__slots__ + ("_json",))


    @property
    def json(self):
        return self._json

    @json.setter
    def json(self, value):
        self._json = value
        self.body = json.dumps(value, indent=4)

def error_handler(ex, req, resp, params):
    raise HTTPBadRequest(type(ex).__name__, str(ex))

class TODOException(HTTPError):

    def __init__(self, **kwargs):
        super(TODOException, self).__init__(status.HTTP_NOT_IMPLEMENTED, **kwargs)

    @property
    def has_representation(self):
        return False
