import json
from pathlib import Path

import falcon

from .tools import JsonRequest, JsonResponse, error_handler
from .controllers import *

class AboutResource():

    def on_get(self, req, resp):
        r = {"about": {
                "name": "Karu Media API",
                "version": "1",
                "docs": "TODO"
                }
            }
        r.update({"endpoints":[
                        {"url":"/",
                        "method":"GET",
                        "description":"About this API"},
                        {"url":"/movies",
                        "method":"GET",
                        "description":"All movies on this server"},
                        {"url":"/movies/{movie}",
                        "method":"GET",
                        "description":"Movie details"},
                        {"url":"/movies/{movie}/stream",
                        "method":"GET",
                        "description":"Returns list of stream urls for the movie"},
                        {"url":"/magnet",
                        "method":"POST",
                        "description":"Add a movie via magnet hash"}
                    ]})

        resp.body = json.dumps(r, indent=4)


app = application = falcon.API(request_type=JsonRequest, response_type=JsonResponse)
app.add_error_handler(ValueError, error_handler)
app.add_route("/", AboutResource())

path = Path("/home/arti/Videod")

app.add_route("/movies", MoviesCollection(path))
app.add_route("/movies/{movie}", MoviesResource(path))
app.add_route("/movies/{movie}/stream", MovieStreamUrlResource(path))

app.add_route("/magnet", MagnetResource())
