
import json
import datetime

from falcon import Request as FalconRequest
from falcon import Response as FalconResponse
from falcon.errors import HTTPBadRequest, HTTPMissingParam, HTTPError, HTTPNotFound
import falcon.status_codes as status
from bson.objectid import ObjectId
from mongoengine import DoesNotExist

class BSONDumps(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.timestamp()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

dumps = BSONDumps(indent=4).encode


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
        self.body = dumps(value)

def error_handler(ex, req, resp, params):
    if type(ex).__name__ == DoesNotExist.__name__:
        raise HTTPNotFound(title=type(ex).__name__, description=str(ex))
    else:
        raise HTTPBadRequest(type(ex).__name__, str(ex))

class TODOException(HTTPError):

    def __init__(self, **kwargs):
        super(TODOException, self).__init__(status.HTTP_NOT_IMPLEMENTED, **kwargs)

    @property
    def has_representation(self):
        return False
